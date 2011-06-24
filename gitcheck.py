#!/bin/env python

import pynotify
import os
from Repository import Repository
from time import sleep

_CONFIG = {"MAXDEPTH"        : 20,
           "GIT_PATH"        : "/usr/bin",
           "project_folders" : ['~/projects/',],
           "icon"            : "git.svg",
           "check_freq"      : 1800}

def find_repo(folder, maxdepth=-1):
  results = []
  if maxdepth == 0:
    return results
  folder = os.path.expanduser(folder)
  for item in os.listdir(folder):
    full_item = os.path.join(folder, item)
    if os.path.isdir(full_item):
      if item == ".git":
        results.append(folder)
      else:
        results += find_repo(full_item,maxdepth-1)
  return results

def show_message(title, message,icon="git.svg"):
  icon = os.path.join(os.getcwd(),icon)
  message = message.replace('&', '&amp;')
  message = message.replace('<', '&lt;')
  message = message.replace('>', '&gt;')

  print "%s: %s"%(title, message)
  msg = pynotify.Notification(title, 
                              message,
                              icon)
  try:
    if not msg.show():
      print "Could not display message: (%s) %s"%(title, message)
  except:
    print "Error communicating with notification daemon"
                        

if __name__ == "__main__":
  if not pynotify.init ("icon-summary-body"):
    print "Could not initialize notification system"
    exit(1)

  repos = []
  for project_folder in _CONFIG["project_folders"]:
    raw_repos = find_repo(project_folder, maxdepth=_CONFIG["MAXDEPTH"])
    for raw_repo in raw_repos:
      repo = Repository(raw_repo,GIT_PATH=_CONFIG["GIT_PATH"])
      repos.append(repo)
      for ref in repo.lockedremote:
        show_message("Warning", "%s: remote '%s' is not updatable.  Check that a passwordless SSH key exists for this remote"%(repo.name, ref))

  while True:
    for repo in repos:
      if repo.check_updates():
        for key, update in repo.get_new_updates():
          show_message("Update to %s"%update["repo"], "[%s]\n%s"%(update["ref"],update["desc"]))
    sleep(_CONFIG["check_freq"])
    repo.update_repo()
