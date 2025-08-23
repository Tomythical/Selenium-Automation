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
	WEBSITE_URL              = "https://nsmembers.sswimclub.org.sg/group/pages/book-a-facility"
	LOGIN_USERNAME           = "#_com_liferay_login_web_portlet_LoginPortlet_login"
	LOGIN_PASSWORD           = "#_com_liferay_login_web_portlet_LoginPortlet_password"
	SIGN_IN_BTN              = "btn-sign-in"
	CLOCK                    = "ui-clock"
	NEXT_WEEK_BTN            = "fa-angle-double-right"
	NEXT_DAY_BTN             = "fa-angle-right"
	DATE_PICKER              = "hasDatepicker"
	BOOK_SESSION_BTN         = "ui-area-btn-success"
	LOADING_TEXT             = "#wrapper"
	COURT_RESERVED_TEXT      = "Reservation created successfully"
	ADVANCED_BOOKING_OVERLAY = "advance-booking-overlay-container"
	TIMEZONE                 = "Asia/Singapore"
	BUCKET_NAME              = "singapore-booking-screenshots"
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
	username_text := os.Getenv("USERNAME")
	password_text := os.Getenv("PASSWORD")

	if username_text == "" || password_text == "" {
		logrus.Error("Username or Password not set in environment variables")
		return
	}

	page.MustElement(LOGIN_USERNAME).MustInput(username_text)
	page.MustElement(LOGIN_PASSWORD).MustInput(password_text)
	page.MustSearch(SIGN_IN_BTN).MustClick()
	logrus.Info("Logging In")
}

func navigateToDate(page *rod.Page) {
	page.MustSearch(CLOCK)
	page.MustScreenshot("images/loading.png")

	sleepCount := 0

	ALLOWED_START_TIME := 7
	if dryRun {
		ALLOWED_START_TIME = 0
	}

	bookingStartTime := getSetHourInTimezone(ALLOWED_START_TIME, TIMEZONE)

	for {
		if sleepCount >= 180 {
			logrus.Error("Sleep count exceeded 3 minutes")
			sleepCount += 1
			return
		}

		timezoneTime, err := getCurrentTimeInTimezone(TIMEZONE)
		if err != nil {
			panic(err)
		}

		if timezoneTime.After(bookingStartTime) {
			logrus.Info("Time is past 7 AM.")
			break
		} else {
			sleepCount += 1
			logrus.Infof("Sleep count: %v", sleepCount)
		}

		time.Sleep(time.Second * 1)
	}

	loc, err := time.LoadLocation(TIMEZONE)
	if err != nil {
		panic(err)
	}

	tomorrow := time.Now().In(loc).AddDate(0, 0, 1).Format("02/01/2006")
	weekAhead := time.Now().In(loc).AddDate(0, 0, 7).Format("02/01/2006")

	if !dryRun {
		logrus.Debug("Clicking Next Week")
		page.MustSearch(NEXT_WEEK_BTN).MustParent().MustClick()

		jsCondition := fmt.Sprintf(`() => {
        const el = document.querySelector('[class*="%s"]');
        return el && el.value === "%s";
      }`, DATE_PICKER, weekAhead)
		page.MustSearch(DATE_PICKER).MustWait(jsCondition)
		page.MustScreenshot("images/court_booking.png")

		logrus.Debugf("Current Day: %v", page.MustSearch(DATE_PICKER).MustText())
	} else {
		logrus.Debug("Clicking Next Day")
		page.MustSearch(NEXT_DAY_BTN).MustParent().MustClick()

		jsCondition := fmt.Sprintf(`() => {
        const el = document.querySelector('[class*="%s"]');
        return el && el.value === "%s";
      }`, DATE_PICKER, tomorrow)
		page.MustSearch(DATE_PICKER).MustWait(jsCondition)

		logrus.Debugf("Current Day: %v", page.MustSearch(DATE_PICKER).MustText())
	}

	advanced_overlay_booking, _ := page.Timeout(time.Second).Search(ADVANCED_BOOKING_OVERLAY)
	if advanced_overlay_booking != nil {
		logrus.Info("Clicked Next Week too soon. Unable to book")
		panic(fmt.Errorf("clicked next week too soon. unable to book"))
	}
}

func chooseCourt(page *rod.Page) (court int, err error) {
	logrus.Info("Choosing court")
	tableRow := startTime - 7
	courtPreference := []int{4, 5, 3, 1, 2, 6}

	for _, court := range courtPreference {
		courtFormatted := fmt.Sprintf("#t%vc%v", tableRow, court-1)
		logrus.Debugf("Court ID: %v", courtFormatted)

		courtElement, err := page.Timeout(time.Second / 10).Element(courtFormatted)
		if err != nil {
			logrus.Debugf("Cannot find court %v", court)
			continue
		}

		if courtElement.MustText() == "" {
			logrus.Infof("Clicking Court %v", court)
			courtElement.MustWaitVisible()
			err := rod.Try(func() {
				courtElement.MustClick()
			})
			if err != nil {
				logrus.Debugf("Could not click court %v. Skipping...", court)
				continue
			}

			return court, nil
		} else {
			logrus.Infof("Court %v is not available: %v", court, courtElement.MustText())
		}
	}
	return -1, fmt.Errorf("no courts available")
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

	date, err := getCurrentTimeInTimezone(TIMEZONE)
	formattedDate := date.Format("Monday - 02-01-06")
	if err != nil {
		panic(err)
	}

	if courtErr != nil {
		logrus.Infof("No courts are available")
		logrus.Infof("Uploading File")
		err := uploadFile(BUCKET_NAME, formattedDate, "images/court_booking.png")
		if err != nil {
			logrus.Errorf("Error uploading file: %v", err)
		}
		return
	}

	if dryRun && !book {
		logrus.Infof("Booking Page Reached. Ending Automation")
		err := uploadFile(BUCKET_NAME, formattedDate, "images/loading.png")
		if err != nil {
			logrus.Errorf("Error uploading file: %v", err)
		}
		return
	}

	page.MustSearch(BOOK_SESSION_BTN).MustClick()
	logrus.Infof("Court %v has been booked for %v:00", courtNumber, startTime)
	page.Timeout(time.Second * 8).MustSearch(COURT_RESERVED_TEXT)

	fileErr := uploadFile(BUCKET_NAME, formattedDate, "images/loading.png")
	if fileErr != nil {
		logrus.Errorf("Error uploading file: %v", err)
	}
}
