package main

import (
	"fmt"
	"time"

	"github.com/sirupsen/logrus"
)

func parseTimeString(timeStr string) (time.Time, error) {
	layouts := []string{"15:04:05", "03:04:05", "3:04:05 AM", "3:04:05 PM"}

	for _, layout := range layouts {
		logrus.Debugf("Parsing timee %s with layout %s", timeStr, layout)
		parsedTime, err := time.Parse(layout, timeStr)
		if err == nil {
			return parsedTime, err
		}
	}

	return time.Time{}, fmt.Errorf("unable to parse time string: %s", timeStr)
}
