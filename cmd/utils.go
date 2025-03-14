package main

import (
	"fmt"
	"time"
)

func parseTimeString(timeStr string) (time.Time, error) {
	layouts := []string{"03:04:05", "3:04:05 AM"}

	for _, layout := range layouts {
		parsedTime, err := time.Parse(layout, timeStr)
		if err == nil {
			return parsedTime, err
		}
	}

	return time.Time{}, fmt.Errorf("unable to parse time string: %s", timeStr)
}
