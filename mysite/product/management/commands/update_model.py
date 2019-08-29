import os
import sys
import requests
import pickle
from django.core.management.base import BaseCommand,CommandError
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist



model_to_url_dict ={'unit':'unit',
                    'datatype':'data-type',
                    'attribute':'attribute',
                    'trademark':'trademark',
                    'country':'country',
                    'option_item':'option',
                    'category':'category',
                    'modifier':'modifier',
                    'item':'item',
                    'itemcategory':'item-category',
                    'itemmodifier': 'item-modifier',
                    'itemattribute':'item-attribute',
                    }


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 2)
    bar = '█' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


class Command (BaseCommand):
    help = 'Test how to make custom manage command'
    tmp_file = 'token.tmp'
    auth_token = dict()

    def handle(self, *args, **options):
        try:
            url = "https://www.sima-land.ru/api/v5/category"
            self.get_auth_token(url)
            self.auth_token["Accept"] = "application/vnd.simaland.item-category+json"
            self.load_table(['itemcategory',], start_page=107086)
            # self.get_from_db_or_api('category', 700104742)

        except Exception as ex:
            raise CommandError('test command error %s' % ex)

    def get_auth_token(self, url="https://www.sima-land.ru/api/v5/category"):
        if os.path.isfile(self.tmp_file):
            with open(self.tmp_file, mode='rb') as token_file:
                self.stdout.write(self.style.SUCCESS('Read token from file'))
                self.auth_token = pickle.load(token_file)
            r = requests.get(url=url, headers=self.auth_token)
            if r.status_code != 200:
                if r.json()['code'] == 'unauthorized':
                    self.stdout.write(self.style.SUCCESS(r.text))
                    while r.status_code != 200:
                        self.stdout.write("Wrong token\n Get new.")
                        self.auth_token['Authorization'] = self.update_auth()
                        r = requests.get(url=url, headers=self.auth_token)
                    with open(self.tmp_file, mode='wb') as token_file:
                        pickle.dump(self.auth_token, token_file)
                        self.stdout.write('New token saved to file')
                else:
                    raise CommandError('Unexpected error while getting auth token')
            else:
                self.stdout.write('Loaded from file token is valid')
        else:
            self.stdout.write(self.style.SUCCESS('File not found'))
            with open(self.tmp_file, mode='wb') as token_file:
                self.auth_token['Authorization'] = self.update_auth()
                r = requests.get(url=url, headers=self.auth_token)
                if r.status_code == 204 or r.status_code == 200 :
                    self.stdout.write(self.style.SUCCESS('save token in file'))
                    pickle.dump(self.auth_token, token_file)
                    token_file.close()
                else:
                    raise ConnectionRefusedError()

    def update_auth(self):
        payload = {"email": "rufusoiddandr@gmail.com",
                   "password": "Ja4TGjxB",
                   "phone": "+375297614812",
                   "regulation": True}
        signin_url = "https://www.sima-land.ru/api/v5/signin"
        r = requests.post(url=signin_url, json=payload)
        if r.status_code == 204:
            self.stdout.write('new token was received')
            return r.headers['Authorization']
        else:
            return ''


    def load_table(self,table_list=None, start_page=1):
        par = dict()
        # for model_name in apps.all_models['product'].keys():
        if table_list is None:
            table_list = list(model_to_url_dict.keys())
        for model_name in table_list:
            page = start_page
            object_counter = 0
            url = 'https://www.sima-land.ru/api/v5/' + model_to_url_dict[model_name]
            self.stdout.write(str(url))
            while True:
                par["p"] = page
                req = requests.get(url=url, headers=self.auth_token, params=par)
                if req.status_code != 200:
                    if req.json()['code'] != 'unauthorized':
                        self.stdout.write(self.style.SUCCESS(f"Downloading {model_name} table is Done"))
                        self.stdout.write(self.style.SUCCESS(f"the last page number is {page}"))
                        break
                    else:
                        self.get_auth_token(self, url)
                        req = requests.get(url=url, headers=self.auth_token, params=par)
                for row in req.json():
                    # self.stdout.write('type %s --> %s'%(model_name, str(row)))
                    if apps.all_models['product'][model_name].objects.filter(pk=int(row['id'])).count():
                        pass
                    else:
                        self.create_object(model_name, row)
                        object_counter += 1
                page += 1
                progress(page, 109355, str(object_counter)+' models has been created, page = '+str(page)+' ')

    def create_object(self, model_name, row):
        # self.stdout.write(self.style.SUCCESS('create obj of model %s  data is %s' % (model_name,row)))
        obj = apps.all_models['product'][model_name](**self.prepare_request(model_name, row))
        obj.save()
        return obj

    def get_from_db_or_api(self, model_name, table_id):
        table_id = int(table_id)
        try:
            query_result = apps.all_models['product'][model_name].objects.get(pk=table_id)
            # self.stdout.write(self.style.SUCCESS('query_result for model  %s is %s'% (model_name, query_result)))
            return query_result
        except ObjectDoesNotExist:
            # self.stdout.write(self.style.SUCCESS('obj %s in model %s does not exist' % (str(table_id), model_name)))
            url = 'https://www.sima-land.ru/api/v5/' + model_to_url_dict[model_name]+'/'+str(table_id)
            # self.stdout.write(self.style.SUCCESS('req stat %s in model %s does not exist' % (str(1), url)))
            req = requests.get(url=url, headers=self.auth_token)

            created_obj = self.create_object(model_name, req.json())
            # self.stdout.write(self.style.SUCCESS('created_obj %s'% created_obj))
            return created_obj

    def update_model(self):
        pass


    def prepare_request(self, model, row):
        row_copy = row.copy()
        if model == 'attribute':
            data_type_id = self.get_from_db_or_api('datatype', row_copy['data_type_id'])
            unit_id = self.get_from_db_or_api('unit', row_copy['unit_id'])
            row_copy['data_type_id'] = data_type_id
            row_copy['unit_id'] = unit_id
            return row_copy
        elif model == 'item':
            country_id = self.get_from_db_or_api('country', row_copy['country_id'])
            nested_unit_id = self.get_from_db_or_api('unit', row_copy['nested_unit_id'])
            unit_id = self.get_from_db_or_api('unit', row_copy['unit_id'])
            trademark_id = self.get_from_db_or_api('trademark', row_copy['trademark_id'])
            row_copy['country_id'] = country_id
            row_copy['unit_id'] = unit_id
            row_copy['nested_unit_id'] = nested_unit_id
            row_copy['trademark_id'] = trademark_id
            return row_copy
        elif model == 'itemcategory':
            item_id = self.get_from_db_or_api('item', row_copy['item_id'])
            category = self.get_from_db_or_api('category', row_copy['category_id'])
            row_copy['item_id'] = item_id
            row_copy['category_id'] = category
            return row_copy
        elif model == 'itemmodifier':

            item_id = self.get_from_db_or_api('item', row_copy['item_id'])
            modifier_id = self.get_from_db_or_api('modifier', row_copy['modifier_id'])
            row_copy['item_id'] = item_id
            row_copy['modifier_id'] = modifier_id
            return row_copy
        elif model =='itemattribute':
            self.stdout.write(self.style.SUCCESS(str(row_copy)))
            attribute_id = self.get_from_db_or_api('attribute', row_copy['attribute_id'])
            item_id = self.get_from_db_or_api('item', row_copy['item_id'])
            option_item = self.get_from_db_or_api('option_item', row_copy['option_value'])
            row_copy['attribute_id'] = attribute_id
            row_copy['item_id'] = item_id
            row_copy['option_value'] = option_item
            return row_copy

        else:
            return row_copy

