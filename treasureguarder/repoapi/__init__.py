# -*- coding: utf-8 -*-

from .repoapi import *
from .giteaapi import GiteaApi
from .githubapi import GithubApi

repoapi.register("gitea", GiteaApi)
repoapi.register("github", GithubApi)
