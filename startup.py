# -*- coding: utf-8 -*-
"""
pyRevit Startup Script for Riyan Plugin
Checks for updates on GitHub and notifies the user.
"""
import ssl
import json
import urllib2
import os
from pyrevit import forms

def check_for_updates():
    try:
        # Get local commit hash
        plugin_dir = os.path.dirname(__file__)
        head_file = os.path.join(plugin_dir, ".git", "refs", "heads", "main")
        
        if not os.path.exists(head_file):
            return
            
        with open(head_file, "r") as f:
            local_commit = f.read().strip()
            
        # Get remote commit hash from GitHub API
        url = "https://api.github.com/repos/udarieimalsha/TestRiyanPlugin/commits/main"
        
        # Bypass SSL verification issues in IronPython older versions
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'pyRevit-RiyanPlugin')
        
        response = urllib2.urlopen(req, context=ctx)
        data = json.loads(response.read())
        remote_commit = data['sha']
        
        # If hashes don't match, we have an update!
        if local_commit != remote_commit:
            forms.alert(
                "A new update is available. Please click the Update button in the pyRevit extensions menu to install it!",
                title="Riyan Plugin Update Available 🚀",
                warn_icon=False
            )
            
    except Exception:
        # If offline or API rate-limited, fail silently so we don't break Revit startup
        pass

# Run the update check when Revit starts
check_for_updates()
