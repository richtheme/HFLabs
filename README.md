## Test Task for Golang developer for HFLabs

В [базе знаний](https://confluence.hflabs.ru/pages/viewpage.action?pageId=1181220999) есть информация о кодах ответа нашего API.

Необходимо написать скрипт, который парсит эту табличку и переносит ее в гуглодоку. Предусмотреть, что в будущем необходимо будет синхронизировать данные в гуглодоке, если что-то изменится в базе знаний.

В результате нужно прислать:
ссылку на код на гитхабе;
ссылку на гуглодоку с перенесенной табличкой;
информацию, сколько времени заняло выполнение задания.

Предпочтительный язык для выполнения задания — go. Допустимые языки — python, ruby.

## Order of execution and elapsed time
- Python: 3 hours (1h15min connect to Google API and test, 15min scraping, 1h writing to spreadsheet, 30min commenting and beautifying the code)
- Golang: 4.5 hours (1h setting Google API, 1h scraping, 1.5h writing functions, 1h commenting and beautifying)
- Ruby: 2.5 hours (35min scraping, 45min setting Google API, 50min writing to spreadsheet, 20min beautifying)