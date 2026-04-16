#!/bin/bash
export OPENROUTER_API_KEY=$(python3 -c 'import json;print(json.load(open("/root/.openclaw/openclaw.json"))["env"]["OPENROUTER_API_KEY"])')
cd /root/sites/video-generator
python3 generate_short.py "$@"
