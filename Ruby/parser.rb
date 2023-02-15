require 'nokogiri'
require 'httparty'
require 'byebug'
require 'google/apis/sheets_v4'
require 'googleauth'


def scraper
	# Scrapping data and returning array with values for easy writing to table
	url = "https://confluence.hflabs.ru/pages/viewpage.action?pageId=1181220999"
	unparsed_html = HTTParty.get(url)
	page = Nokogiri::HTML(unparsed_html)
	values = Array.new

	table = page.css('table.confluenceTable')
	trs_array = Array.new

	ths = table.css('th')
	tds_array = Array.new
	ths.each do |th|
		tds_array.push(th.text)
	end
	trs_array.push(tds_array)

	trs = table.css('tr')[1..]
	trs.each do |tr|
		tds = tr.css('td')
		tds_array = Array.new
		tds.each do |td|
			tds_array.push(td.text)
		end
		trs_array.push(tds_array)
	end

	return trs_array
end


def write_spreadsheet(values)
	# Authenticate and write data to the spreadsheet
	SHEET_NAME = "Sheet 1st"
	ALPHABET = ["A", "B", "C", "D", "E", "F"]
	SPREADSHEET_ID = "1H-wsDEbXGO22jkKrYMZM9TlbCS7P1Pf5gNs_y4tSW2g"
	
	scope = 'https://www.googleapis.com/auth/drive'
	authorizer = Google::Auth::ServiceAccountCredentials.make_creds(
		json_key_io: File.open('credentials.json'),
		scope: scope)
	
	service = Google::Apis::SheetsV4::SheetsService.new
	service.authorization = authorizer

	# range = "Sheet 1st!A1:F"
	# result = service.get_spreadsheet_values(SPREADSHEET_ID, range)
	
	range = SHEET_NAME + "!A1:" + ALPHABET[values[0].length() - 1]
	 + values.length().to_s()

	value_range_object = {
		"major_dimension": "ROWS",
		"values": values
	}

	# Resetting table values
	service.clear_values(SPREADSHEET_ID, SHEET_NAME + "!A1:Z99")
	
	# Writing data to the table
	service.update_spreadsheet_value(SPREADSHEET_ID, range,
		value_range_object, value_input_option: 'USER_ENTERED')
end


if __FILE__ == $0
	# Entrypoint for this file
	values = scraper
	write_spreadsheet(values)
end
