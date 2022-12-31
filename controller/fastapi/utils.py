import os

from fastapi import FastAPI
from fastapi.routing import APIRoute


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


class APISchema:
    class URL:
        def __init__(self, url: str, method: str, data: dict):
            self.url = url
            self.method = method
            self.data = data

        def __str__(self):
            return f'{self.method.upper()} {self.url}'

        def __repr__(self):
            return self.__str__()

        def to_js(self):
            prop_name = 'props'
            return {
                'template': f"export const {self.data.get('operationId', '').upper()} = {prop_name} => BASE_URL.{self.method.lower()}('{self.url}', {prop_name})",
                'file': self.data.get('tags', ['index']),
                'description': self.data.get('description', '')
            }

    def __init__(self, schema: dict):
        self.schema = schema
        self.info = {}
        self.urls = []
        self.parse_info()
        self.parse_paths()

    def parse_info(self):
        self.info = self.schema.get('info')

    def parse_paths(self):
        for url, methods in self.schema.get('paths').items():
            for method, data in methods.items():
                self.urls.append(APISchema.URL(url, method, data))

    def generate_js(self, path: str):
        os.makedirs(path, exist_ok=True)
        files = {}
        for api in self.urls:
            response = api.to_js()
            for file in response.get('file'):
                files.setdefault(file.lower(), [])
                files[file.lower()].append(response)
        for file, urls in files.items():
            with open(path + os.sep + file + '.js', 'w') as f:
                api_urls = [item.get('template') for item in urls]
                if file != 'index':
                    api_urls = ['import {BASE_URL} from "./index";'] + api_urls
                else:
                    api_urls = ['export const BASE_URL = {};'] + api_urls
                f.write('\n'.join(api_urls))
