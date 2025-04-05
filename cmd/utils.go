package main

import (
	"time"

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
