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

        try:
            org_opts = giteapy.CreateOrgOption(username=owner)
            org_opts.visibility = "private"
            org_opts.repo_admin_change_team_access = True
            org_api.org_create(organization=org_opts)
        except giteapy.rest.ApiException:
            pass

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

    def get_group(self, group: str) -> Dict:
        api = giteapy.OrganizationApi(self._client)

        try:
            info = {"description": api.org_get(group).description}
            return info
        except giteapy.rest.ApiException as e:
            if e.status == 404:
                api = giteapy.UserApi(self._client)
                user_info = api.user_get(group)
                if hasattr(user_info, "description"):
                    info = {"description": api.user_get(group).description}
                else:
                    info = {"description": ""}

                return info

            raise RepoApiError(str(e))

    def edit_group(self, group: str, desc: str):
        api = giteapy.OrganizationApi(self._client)

        body = {
            "description": desc,
        }
        api.org_edit(group, body)
