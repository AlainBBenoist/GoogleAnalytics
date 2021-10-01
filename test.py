# Google libraries
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build


class GAReporter() :
    def __init__(self, keyfile) :
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name('analytics-dibutade.json', ['https://www.googleapis.com/auth/analytics.readonly'])
        # Build the service object.
        self.analytics = build('analyticsreporting', 'v4', credentials=self.credentials)

    def report(self, view_id, start_date, end_date, metrics=None, dimensions=None) :
        if not metrics:
            metrics = [ 'users', 'newUsers', 'sessions', 'sessionsPerUser', 'pageviews', 'pageviewsPerSession', 'avgSessionDuration', 'sessionsPerUser', 'bounceRate', ]
        if not dimensions:
            dimensions = [  'medium', 'source', ] # 'deviceCategory',
            
        body = {
            'reportRequests': [
                {   'viewId': view_id,
                    'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                    'metrics': [ { "expression": 'ga:'+metric } for metric in metrics ],
                    'dimensions':[ { "name": 'ga:'+dimension } for dimension in dimensions ],
                }
            ]
        }

        response = self.analytics.reports().batchGet(body=body).execute()
        return response

    def print(self, response):
        row_list = []
        # Get each collected report
        for report in response.get('reports', []):
            # Set column headers
            column_header = report.get('columnHeader', {})
            dimension_headers = column_header.get('dimensions', [])
            metric_headers = column_header.get('metricHeader', {}).get('metricHeaderEntries', [])
    
            # Get each row in the report
            for row in report.get('data', {}).get('rows', []):
                # create dict for each row
                row_dict = {}
                dimensions = row.get('dimensions', [])
                date_range_values = row.get('metrics', [])

                # Fill dict with dimension header (key) and dimension value (value)
                for header, dimension in zip(dimension_headers, dimensions):
                    row_dict[header] = dimension

                # Fill dict with metric header (key) and metric value (value)
                for i, values in enumerate(date_range_values):
                    for metric, value in zip(metric_headers, values.get('values')):
                    # Set int as int, float a float
                        if ',' in value or '.' in value:
                            row_dict[metric.get('name')] = float(value)
                        else:
                            row_dict[metric.get('name')] = int(value)

                row_list.append(row_dict)
        return row_list

if __name__ == '__main__':
    import datetime
    KEYFILE='analytics-dibutade.json'
    VIEW_ID='141366074'
    START_DATE='2021-01-01'
    END_DATE='2021-08-31'

    # Calculate yesterdate
    start_date = datetime.date.today() - datetime.timedelta(days=1)
    print(start_date.isoformat())

    # Create a Google Analytics reporter
    ga = GAReporter(KEYFILE)

    # Get a view 
    response = ga.report(VIEW_ID, START_DATE, END_DATE)
    #print(response)
    #for result in ga.print(response):
    #    print('{:32.32s} {:32.32s} {:d}'.format(result['ga:medium'], result['ga:source'], result['ga:sessions']))
    print('===============================')
    response = ga.report(VIEW_ID, start_date.isoformat(), start_date.isoformat(), metrics=['pageviews', ], dimensions=['pagePath',])
    #print(response)
    for result in ga.print(response):
        print('{:96.96s} {:d}'.format(result['ga:pagePath'], result['ga:pageviews']))

    print('===============================')
    response = ga.report(VIEW_ID, start_date.isoformat(), start_date.isoformat(), metrics=['totalEvents', ], dimensions=['eventAction',])
    #print(response)
    for result in ga.print(response):
        print('{:96.96s} {:d}'.format(result['ga:eventAction'], result['ga:totalEvents']))
        
    print('===============================')
    response = ga.report(VIEW_ID, start_date.isoformat(), start_date.isoformat(), metrics=['impressions', 'adClicks', 'adCost' ], dimensions=['adGroup',])
    #print(response)
    for result in ga.print(response):
        print('{:96.96s} {:8d} {:8d} {:6.2f}'.format(result['ga:adGroup'], result['ga:impressions'], result['ga:adClicks'], result['ga:adCost']))

    print('===============================')
    response = ga.report(VIEW_ID, start_date.isoformat(), start_date.isoformat(), metrics=['searchResultViews' ], dimensions=['searchKeyword',])
    #print(response)
    for result in ga.print(response):
        print('{:96.96s} {:8d}'.format(result['ga:searchKeyword'], result['ga:searchResultViews']))
        

