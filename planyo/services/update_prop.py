import csv
import logging

import requests

from planyo.models import ApiKey

logger = logging.getLogger(__name__)


class PlanyoIntegrationException(Exception):
    pass


class UpdateUserComment:

    def __init__(self, environment):
        api_key = ApiKey.objects.filter(environment=environment)
        if not api_key.exists():
            raise Exception('No such environment')
        self.api_key = api_key.first().api_key
        # self.api_key = 'api_key_placeholder'
        self.base_url = 'https://www.planyo.com/rest/'

    def api_call(self, params, endpoint=''):
        logger.info(f'request to {self.base_url + endpoint} with {params}')
        params['api_key'] = self.api_key
        resp = requests.get(self.base_url + endpoint, params=params)
        logger.info(f'response {resp.status_code} {resp.text}')
        return resp

    def execute(self):
        self.update_prop_user_comment('4384490', 'tes2t')

    def bulk_update(self, csv_file):
        reader = csv.DictReader(csv_file.split('\n'), delimiter=',')
        csv_rows = list(reader)
        logger.info(f'Importing csv with {len(csv_rows)} rows')
        if len(csv_rows) == 0:
            logger.warning('csv empty')
            return ['csv jest puste. pamiętaj o kolumnach $(user_id) i $(prop_user_comment)']
        result = []
        for row in csv_rows:
            if '$(user_id)' not in row or '$(prop_user_comment)' not in row:
                logger.warning('csv incorrect. No valid headers')
                return [
                    f"niepoprawna csv. dodaj kolumny: $(user_id) i $(prop_user_comment). Zwróć uwagę na spacje. Rozpoznane kolumny: {list(csv_rows[0].keys())}"]
            resp = self.update_prop_user_comment(row['$(user_id)'], row['$(prop_user_comment)'])
            result.append(resp)
        logger.info(f'Csv imported')
        return result

    def update_prop_user_comment(self, user_id, comment):
        user_info = self.api_call({'method': 'get_user_data', 'user_id': user_id, 'detail_level': 4}).json()
        if 'data' not in user_info:
            if 'response_code' in user_info and user_info['response_code'] == 1:
                raise PlanyoIntegrationException(
                    '[{}]: {}'.format(user_info['response_code'], user_info['response_message']))
            return 'nie ma takiego user_id: {}. {}'.format(user_id, user_info.get('response_message', ''))
        old_comment = user_info['data'].get('properties', {}).get('comment', '')
        self.api_call({'method': 'modify_user', 'user_id': user_id, 'prop_user_comment': comment})
        return 'user_id {}: zmiana user_prop_comment z "{}" do "{}" '.format(user_id, old_comment, comment)
