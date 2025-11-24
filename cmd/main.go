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
	BOOK_SESSION_BTN         = "btn-save"
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

	err := rod.Try(func() {
		page.MustElement(LOGIN_USERNAME).MustInput(username_text)
		page.MustElement(LOGIN_PASSWORD).MustInput(password_text)
		page.MustSearch(SIGN_IN_BTN).MustClick()
	})
	if err != nil {
		logrus.Errorf("Error logging in: %v", err)
	}

	logrus.Info("Logging In")
}

func navigateToDate(page *rod.Page) {
	err := rod.Try(func() {
		page.MustSearch(CLOCK).MustWaitVisible()
	})
	if err != nil {
		logrus.Errorf("Error waiting for clock: %v", err)
	}

	sleepCount := 0

	ALLOWED_START_TIME := 7
	if dryRun {
		ALLOWED_START_TIME = 0
	}

	bookingStartTime := getSetHourInTimezone(ALLOWED_START_TIME, TIMEZONE)

	for {
		if sleepCount >= 180 {
			logrus.Error("Sleep count exceeded 3 minutes")
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
		err := rod.Try(func() {
			page.MustSearch(NEXT_WEEK_BTN).MustParent().MustClick()

			// To debug flaky issues like this, you can add more detailed logging and artifacts:
			// 1. Log precise timestamps: logrus.Debugf("Clicked at %v", time.Now())
			// 2. Take screenshots: page.MustScreenshot("images/after-click.png")
			// 3. Check the browser's Network tab in devtools to see if a request is slow.

			// The flakiness is likely due to an AJAX call updating the calendar.
			// We will now wait for the loading spinner to appear and then disappear.
			// This selector is a guess for a common loading spinner in JSF/PrimeFaces.
			// If the script is still flaky, inspect the page to find the correct selector.
			const loadingSelector = "div.ui-icon-loading"

			// Wait for the loading spinner to appear. A short timeout is fine.
			// If it doesn't appear, the page may have loaded too fast to see it.
			if spinner, err := page.Timeout(3 * time.Second).Element(loadingSelector); err == nil {
				logrus.Debug("Loading indicator appeared. Waiting for it to disappear.")
				spinner.MustWaitInvisible() // Wait for it to disappear (default timeout).
				logrus.Debug("Loading indicator disappeared.")
			} else {
				logrus.Debug("Loading indicator did not appear, assuming fast load and continuing.")
			}
		})
		if err != nil {
			// If the error happens here, it could be a timeout from MustWaitInvisible.
			logrus.Errorf("Error clicking or waiting for next week button to load: %v", err)
			page.MustScreenshot("images/next-week-load-error.png")
		}

		// Wait for the date picker to update to the expected weekAhead date
		jsCondition := fmt.Sprintf(`() => {
        const el = document.querySelector('[class*="%s"]');
        return el && el.value === "%s";
      }`, DATE_PICKER, weekAhead)
		err = rod.Try(func() {
			page.Timeout(10 * time.Second).MustSearch(DATE_PICKER).MustWait(jsCondition)
		})
		if err != nil {
			logrus.Errorf("Error waiting for date picker after clicking Next Week: %v", err)
			page.MustScreenshot("images/next_week_datepicker_timeout.png")
		}
		page.MustScreenshot("images/court_booking.png")

		logrus.Debugf("Current Day: %v", page.MustSearch(DATE_PICKER).MustText())
	} else {
		logrus.Debug("Clicking Next Day")
		err := rod.Try(func() {
			page.MustSearch(NEXT_DAY_BTN).MustParent().MustClick()
		})
		if err != nil {
			logrus.Errorf("Error clicking next day button: %v", err)
		}
		// Wait for the date picker to update to the expected tomorrow date
		jsCondition := fmt.Sprintf(`() => {
        const el = document.querySelector('[class*="%s"]');
        return el && el.value === "%s";
      }`, DATE_PICKER, tomorrow)
		err = rod.Try(func() {
			page.Timeout(60 * time.Second).MustSearch(DATE_PICKER).MustWait(jsCondition)
		})
		if err != nil {
			logrus.Errorf("Error waiting for date picker after clicking Next Day: %v", err)
			page.MustScreenshot("images/next_day_datepicker_timeout.png")
		}
		page.MustScreenshot("images/court_booking.png")
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

		courtElement, err := page.Timeout(time.Second * 2).Element(courtFormatted)
		if err != nil {
			logrus.Debugf("Cannot find court %v", court)
			continue
		}

		courtText, err := courtElement.Text()
		if err != nil {
			logrus.Infof("Could not get text from Court %v", court)
			logrus.Debugf("Court %v Element: %v", court, courtElement)
			continue
		}
		if courtText == "" {
			logrus.Infof("Clicking Court %v", court)
			courtElement.MustWaitVisible()
			err := rod.Try(func() {
				courtElement.MustClick()
				page.MustSearch(BOOK_SESSION_BTN).MustWaitVisible()
			})
			if err != nil {
				logrus.Debugf("Could not click court %v. Skipping...", court)
				continue
			}

			return court, nil
		} else if courtText == "RESERVED" {
			logrus.Infof("Court %v is already reserved", court)
		} else {
			logrus.Infof("Court %v is not available: %v", court, courtElement.MustText())
		}
	}
	return -1, fmt.Errorf("no courts available")
}

func main() {
	var err error
	argParser()
	setUp()

	var browser *rod.Browser
	var page *rod.Page

	// recover + screenshot on panic
	defer func() {
		if r := recover(); r != nil {
			logrus.Errorf("panic recovered: %v", r)

			// screenshot and page HTML if page exists (use rod.Try so we don't panic again)
			if page != nil {
				logrus.Info("Taking screenshot of the error")
				_ = rod.Try(func() { page.MustScreenshot("images/panic.png") })
			} else {
				logrus.Info("Page is nil")
			}

			uploadScreenshots(BUCKET_NAME, TIMEZONE)

			// best-effort close browser
			if browser != nil {
				_ = browser.Close()
			}

			os.Exit(1)
		}
	}()

	// create browser and page
	browser = rod.New().MustConnect().NoDefaultDevice().Timeout(time.Second * 300).Trace(true)
	defer func() {
		if err := browser.Close(); err != nil {
			page.MustScreenshot("images/context_timeout.png")
			uploadScreenshots(BUCKET_NAME, TIMEZONE)
			logrus.Errorf("Error closing browser: %v", err)
		}
	}()

	page = browser.MustPage(WEBSITE_URL).MustWindowFullscreen().MustWaitStable()

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

		if !dryRun {
			logrus.Infof("Uploading File")
			err := uploadFile(BUCKET_NAME, formattedDate, "images/court_booking.png")
			if err != nil {
				logrus.Errorf("Error uploading file: %v", err)
			}
		}
		return
	}

	if dryRun && !book {
		logrus.Infof("Booking Page Reached. Ending Automation")
		return
	}

	err = rod.Try(func() {
		logrus.Debugf("Reach Booking Page")
		page.MustScreenshot("images/booking_screen.png")
		page.MustSearch(BOOK_SESSION_BTN).MustClick()
		logrus.Infof("Court %v has been booked for %v:00", courtNumber, startTime)
		page.Timeout(time.Second * 8).MustSearch(COURT_RESERVED_TEXT)
	})
	if err != nil {
		logrus.Errorf("Error booking court: %v", err)
		uploadScreenshots(BUCKET_NAME, TIMEZONE)
	}
}
