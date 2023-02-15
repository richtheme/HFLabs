package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/gocolly/colly"
	"golang.org/x/oauth2/google"
	"google.golang.org/api/option"
	"google.golang.org/api/sheets/v4"
)

func main() {
	// Read credentials
	data, err := os.ReadFile("credentials.json")
	if err != nil {
		log.Fatalf("Unable to read client secret file: %v", err)
		return
	}

	// create api context
	ctx := context.Background()

	// authenticate and get configuration
	config, err := google.JWTConfigFromJSON(data, "https://www.googleapis.com/auth/spreadsheets")
	if err != nil {
		log.Fatalf("Unable to parse client secret file to config: %v", err)
		return
	}

	// create client with config and context
	client := config.Client(ctx)

	// create new service using client
	srv, err := sheets.NewService(ctx, option.WithHTTPClient(client))
	if err != nil {
		log.Fatalf("Unable to retrieve Sheets client: %v", err)
		return
	}

	spreadsheetId := "1H-wsDEbXGO22jkKrYMZM9TlbCS7P1Pf5gNs_y4tSW2g"

	// Convert sheet ID to sheet name.
	response1, err := srv.Spreadsheets.Get(spreadsheetId).Fields("sheets(properties(sheetId,title))").Do()
	if err != nil || response1.HTTPStatusCode != 200 {
		log.Fatalf("Error: %v", err)
		return
	}

	resetTable(spreadsheetId, ctx, srv)
	values := parser()
	updateData(values, spreadsheetId, ctx, srv)

	// Save command line
	var aaa string
	fmt.Scan(&aaa)
}

func parser() [][]interface{} {
	var values [][]interface{}

	c := colly.NewCollector()
	c.OnHTML(".confluenceTable", func(e *colly.HTMLElement) {
		e.ForEach("tr", func(iter int, el *colly.HTMLElement) {
			if iter == 0 {
				values = append(values, []interface{}{el.ChildText("th:nth-child(1)"), el.ChildText("th:nth-child(2)")})
			} else {
				values = append(values, []interface{}{el.ChildText("td:nth-child(1)"), el.ChildText("td:nth-child(2)")})
			}
		})
	})
	c.Visit("https://confluence.hflabs.ru/pages/viewpage.action?pageId=1181220999")
	return values
}

func updateData(values [][]interface{}, spreadsheetId string, ctx context.Context, srv *sheets.Service) {
	alphabet := []string{"A", "B", "C", "D", "E"}
	range2 := fmt.Sprintf("A1:%s%d", alphabet[len(values[0])-1], len(values))
	fmt.Println(range2)
	row1 := &sheets.ValueRange{
		Values: values,
	}
	_, err := srv.Spreadsheets.Values.Update(spreadsheetId, range2, row1).ValueInputOption("USER_ENTERED").Context(ctx).Do()
	if err != nil {
		log.Fatalf("Error: %v", err)
		return
	}
}

func resetTable(spreadsheetId string, ctx context.Context, srv *sheets.Service) {
	rangeAll := "A1:Z"
	rb := &sheets.ClearValuesRequest{}
	_, err := srv.Spreadsheets.Values.Clear(spreadsheetId, rangeAll, rb).Context(ctx).Do()
	if err != nil {
		log.Fatalf("Error: %v", err)
		return
	}
}
