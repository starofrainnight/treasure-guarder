# -*- coding: utf-8 -*-


from typing import Dict


class RepoApiError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class RepoApi(object):
    def __init__(self, access_context) -> None:
        super().__init__()

    def create_repo(self, owner: str, repo_name: str):
        raise NotImplementedError()

    def edit_repo(self, owner: str, repo_name: str, desc: str):
        raise NotImplementedError()

    def get_repo(self, owner: str, repo_name: str) -> Dict:
        raise NotImplementedError()

    def get_group(self, group: str) -> Dict:
        raise NotImplementedError()

    def edit_group(self, group: str, desc: str):
        raise NotImplementedError()


_apis = dict()


def register(type_name: str, klass):
    _apis[type_name] = klass


def get(access_context) -> RepoApi:
    return _apis[access_context["type"]](access_context)
