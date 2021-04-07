# -*- coding: utf-8 -*-

from typing import Dict, overload
import giteapy
import giteapy.rest
from . import repoapi
from .repoapi import RepoApi, RepoApiError


class GiteaApi(RepoApi):
    def __init__(self, access_context) -> None:
        super().__init__(access_context)

        cfg = giteapy.Configuration()
        cfg.host = access_context["api-url"]
        cfg.api_key["access_token"] = access_context["token"]
        cfg.verify_ssl = False

        self._cfg = cfg
        self._client = giteapy.ApiClient(cfg)

    def create_repo(self, owner: str, repo_name: str):

        org_api = giteapy.OrganizationApi(self._client)

        body = {
            "auto_init": False,
            "default_branch": "master",
            "description": "",
            "gitignores": "",
            "issue_labels": "",
            "license": "",
            "name": repo_name,
            "private": True,
            "readme": "",
            "template": False,
            "trust_model": "default",
        }

        org_api.create_org_repo(org=owner, body=body)

    def edit_repo(self, owner: str, repo_name: str, desc: str):
        repo_api = giteapy.RepositoryApi(self._client)

        body = {
            "description": desc,
        }
        repo_api.repo_edit(owner, repo_name, body=body)

    def get_repo(self, owner: str, repo_name: str) -> Dict:
        repo_api = giteapy.RepositoryApi(self._client)

        try:
            repo = {
                "description": repo_api.repo_get(owner, repo_name).description
            }
            return repo
        except giteapy.rest.ApiException as e:
            raise RepoApiError(str(e))
