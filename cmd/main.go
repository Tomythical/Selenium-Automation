package main

import (
	"fmt"
	"time"

	"github.com/go-rod/rod"
	"github.com/sirupsen/logrus"
)

const (
	START_TIME     int    = 18
	WEBSITE_URL    string = "https://nsmembers.sswimclub.org.sg/group/pages/book-a-facility"
	LOGIN_USERNAME        = "#_com_liferay_login_web_portlet_LoginPortlet_login"
	LOGIN_PASSWORD        = "#_com_liferay_login_web_portlet_LoginPortlet_password"
	SIGN_IN_BTN           = "btn-sign-in"
	CLOCK                 = "#_activities_WAR_northstarportlet_\\:activityForm\\:j_idt70"
)

func chooseCourt(page *rod.Page) error {
	logrus.Info("Choosing court")
	tableRow := START_TIME - 7
	courtPreference := []int{4, 5, 3, 1, 2, 6}

	for _, court := range courtPreference {
		courtFormatted := fmt.Sprintf("#t%vc%v", tableRow, court-1)
		logrus.Debugf("Court ID: %v", courtFormatted)

		courtElement, err := page.Timeout(time.Second * 4).Element(courtFormatted)
		if err != nil {
			logrus.Debugf("Cannot find court %v", court)
			continue
		}

		if courtElement.MustText() == "" {
			logrus.Infof("Clicking Court %v", court)
			courtElement.MustWaitVisible()
			courtElement.MustClick()
			return nil
		} else {
			logrus.Infof("Court %v is not available: %v", court, courtElement.MustText())
		}
	}
	return fmt.Errorf("No Courts available")
}

func main() {
	logrus.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
	})
	logrus.SetLevel(logrus.DebugLevel)

	browser := rod.New().MustConnect().NoDefaultDevice().Timeout(time.Second * 30)
	defer browser.Close()

	page := browser.MustPage(WEBSITE_URL).MustWindowFullscreen().MustWaitStable()

	page.MustElement(LOGIN_USERNAME).MustInput("CO41102")
	page.MustElement(LOGIN_PASSWORD).MustInput("Friyana001")
	page.MustSearch(SIGN_IN_BTN).MustClick()
	logrus.Info("Logging In")

	layout := "03:04:05 PM"
	sleepCount := 0
	sevenAM, err := time.Parse(layout, "00:00:00 AM")
	if err != nil {
		logrus.Error("Error parsing 7 AM:", err)
		return
	}

	for {
		el := page.MustElement(CLOCK)
		logrus.Info(el.MustText())

		if sleepCount >= 10 {
			logrus.Error("Sleep count exceeded 2 minutes")
			sleepCount += 1
			return
		}
		if el.MustText() == "" {
			logrus.Debug("Clock has no text")
			time.Sleep(time.Second)
			continue
		}
		clockTime, err := time.Parse(layout, el.MustText())
		if err != nil {
			logrus.Error("Error parsing time:", err)
			return
		}

		if clockTime.After(sevenAM) {
			logrus.Info("Time is past 7 AM.")
			break
		} else {
			sleepCount += 1
			logrus.Infof("Sleep count: %v", sleepCount)
		}

		time.Sleep(time.Second)

	}

	courtErr := chooseCourt(page)
	if courtErr != nil {
		return
	}
	time.Sleep(time.Hour)
}
