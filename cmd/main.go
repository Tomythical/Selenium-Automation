package main

import (
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/go-rod/rod"
	"github.com/joho/godotenv"
	"github.com/sirupsen/logrus"
)

const (
	WEBSITE_URL      = "https://nsmembers.sswimclub.org.sg/group/pages/book-a-facility"
	LOGIN_USERNAME   = "#_com_liferay_login_web_portlet_LoginPortlet_login"
	LOGIN_PASSWORD   = "#_com_liferay_login_web_portlet_LoginPortlet_password"
	SIGN_IN_BTN      = "btn-sign-in"
	CLOCK            = "#_activities_WAR_northstarportlet_\\:activityForm\\:currentTime"
	NEXT_WEEK_BTN    = "#_activities_WAR_northstarportlet_\\:activityForm\\:j_idt100"
	NEXT_DAY_BTN     = "#_activities_WAR_northstarportlet_\\:activityForm\\:j_idt94"
	DATE_PICKER      = "#_activities_WAR_northstarportlet_\\:activityForm\\:j_idt57_input"
	BOOK_SESSION_BTN = "#_activities_WAR_northstarportlet_\\:activityForm\\:j_idt378"
	LOADING_TEXT     = "#wrapper"
)

var (
	startTime int
	dryRun    bool
	book      bool
)

func setUp() {
	logrus.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
	})
	logrus.SetLevel(logrus.DebugLevel)

	err := godotenv.Load()
	if err != nil {
		logrus.Info("No .env file found")
	}
}

func argParser() {
	flag.IntVar(&startTime, "start", 8, "Set session start time")
	flag.BoolVar(&dryRun, "dry", false, "Simulate the run without making any changes")
	flag.BoolVar(&book, "book", false, "Allow for booking when in dry-run mode")

	// Parse the command line flags.
	flag.Parse()

	logrus.Debugf("Start Time: %d\n", startTime)
	if dryRun {
		logrus.Debugf("Dry-run mode enabled")
	} else {
		logrus.Debugf("Dry-run mode disabled")
	}

	if book {
		logrus.Debugf("Will book session today")
	}
}

func logIn(page *rod.Page) {
	page.MustElement(LOGIN_USERNAME).MustInput(os.Getenv("USERNAME"))
	page.MustElement(LOGIN_PASSWORD).MustInput(os.Getenv("PASSWORD"))
	page.MustSearch(SIGN_IN_BTN).MustClick()
	logrus.Info("Logging In")
}

func navigateToDate(page *rod.Page) {
	sleepCount := 0

	ALLOWED_START_TIME := "07:00:00"
	if dryRun {
		ALLOWED_START_TIME = "00:00:00"
	}

	bookingStartTime, err := parseTimeString(ALLOWED_START_TIME)
	if err != nil {
		panic(err)
	}

	for {
		el := page.MustElement(CLOCK)
		logrus.Info(el.MustText())

		if sleepCount >= 180 {
			logrus.Error("Sleep count exceeded 3 minutes")
			sleepCount += 1
			return
		}
		if el.MustText() == "" {
			logrus.Debug("Clock has no text")
			time.Sleep(time.Second)
			continue
		}

		clockTime, err := parseTimeString(el.MustText())
		if err != nil {
			panic(err)
		}

		if clockTime.After(bookingStartTime) {
			logrus.Info("Time is past 7 AM.")
			break
		} else {
			sleepCount += 1
			logrus.Infof("Sleep count: %v", sleepCount)
		}

		time.Sleep(time.Second * 3)
	}

	loc, err := time.LoadLocation("Asia/Singapore")
	if err != nil {
		panic(err)
	}

	tomorrow := time.Now().In(loc).AddDate(0, 0, 1).Format("02/01/2006")
	weekAhead := time.Now().In(loc).AddDate(0, 0, 7).Format("02/01/2006")

	if !dryRun {
		logrus.Debug("Clicking Next Week")
		page.MustElement(NEXT_WEEK_BTN).MustClick()

		jsCondition := fmt.Sprintf(`() => {
        const el = document.querySelector("input#_activities_WAR_northstarportlet_\\:activityForm\\:j_idt65_input");
        return el && el.value === "%s";
      }`, weekAhead)
		page.MustElement(DATE_PICKER).MustWait(jsCondition)

		logrus.Debugf("Current Day: %v", page.MustElement(DATE_PICKER).MustText())
	} else {
		logrus.Debug("Clicking Next Day")
		page.MustElement(NEXT_DAY_BTN).MustClick()

		jsCondition := fmt.Sprintf(`() => {
        const el = document.querySelector("input#_activities_WAR_northstarportlet_\\:activityForm\\:j_idt57_input");
        return el && el.value === "%s";
      }`, tomorrow)
		page.MustElement(DATE_PICKER).MustWait(jsCondition)

		logrus.Debugf("Current Day: %v", page.MustElement(DATE_PICKER).MustText())
	}
}

func chooseCourt(page *rod.Page) (court int, err error) {
	logrus.Info("Choosing court")
	tableRow := startTime - 7
	courtPreference := []int{4, 5, 3, 1, 2, 6}

	for _, court := range courtPreference {
		courtFormatted := fmt.Sprintf("#t%vc%v", tableRow, court-1)
		logrus.Debugf("Court ID: %v", courtFormatted)

		courtElement, err := page.Timeout(time.Second * 5).Element(courtFormatted)
		if err != nil {
			logrus.Debugf("Cannot find court %v", court)
			continue
		}

		if courtElement.MustText() == "" {
			logrus.Infof("Clicking Court %v", court)
			courtElement.MustWaitVisible()
			courtElement.MustClick()
			return court, nil
		} else {
			logrus.Infof("Court %v is not available: %v", court, courtElement.MustText())
		}
	}
	return -1, fmt.Errorf("No Courts available")
}

func main() {
	argParser()
	setUp()

	browser := rod.New().MustConnect().NoDefaultDevice().Timeout(time.Second * 300).Trace(true)
	defer browser.Close()
	page := browser.MustPage(WEBSITE_URL).MustWindowFullscreen().MustWaitStable()

	logIn(page)
	navigateToDate(page)

	courtNumber, courtErr := chooseCourt(page)
	if courtErr != nil {
		logrus.Errorf("No courts are available")
		return
	}

	if dryRun && !book {
		logrus.Infof("Booking Page Reached. Ending Automation")
		return
	}

	page.MustElement(BOOK_SESSION_BTN).MustClick()
	logrus.Infof("Court %v has been booked for %v:00", courtNumber, startTime)
}
