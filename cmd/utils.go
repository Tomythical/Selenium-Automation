package main

import (
	"context"
	"fmt"
	"io"
	"os"
	"time"

	"cloud.google.com/go/storage"
	"github.com/sirupsen/logrus"
)

func getSetHourInTimezone(startHour int, timezone string) time.Time {
	location, err := time.LoadLocation(timezone)
	if err != nil {
		panic(err)
	}

	locationCurrentTime := time.Now().In(location)

	timezoneAdjustedTime := time.Date(locationCurrentTime.Year(), locationCurrentTime.Month(), locationCurrentTime.Day(), startHour, 0, 0, 0, location)
	logrus.Debugf("Today at %v AM in Singapore: %v", startHour, timezoneAdjustedTime)
	return timezoneAdjustedTime
}

func getCurrentTimeInTimezone(timezone string) (time.Time, error) {
	location, err := time.LoadLocation(timezone)
	if err != nil {
		logrus.Errorf("Error loading location: %v", err)
		return time.Time{}, err
	}
	currentTime := time.Now().In(location)
	logrus.Debugf("Current time: %s", currentTime)
	return currentTime, nil
}

func uploadFile(bucket, folder, filePath string) error {
	ctx := context.Background()
	client, err := storage.NewClient(ctx)
	if err != nil {
		return fmt.Errorf("failed to create client: %v", err)
	}
	logrus.Debugf("Creating client")
	defer client.Close()

	// Open local file.
	f, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("os.Open: %w", err)
	}
	defer f.Close()

	objectName := fmt.Sprintf("%s/%s", folder, f.Name())
	wc := client.Bucket(bucket).Object(objectName).NewWriter(ctx)
	// Optionally, set attributes such as the content type.
	wc.ContentType = "application/octet-stream"

	_, cancel := context.WithTimeout(ctx, time.Second*50)
	defer cancel()

	// Copy the file data to Google Cloud Storage.
	if _, err = io.Copy(wc, f); err != nil {
		return fmt.Errorf("io.Copy: %v", err)
	}
	// Close the writer and finalize the upload.
	if err = wc.Close(); err != nil {
		return fmt.Errorf("Writer.Close: %v", err)
	}

	logrus.Infof("File %s uploaded to bucket %s as %s\n", filePath, bucket, objectName)
	return nil
}
