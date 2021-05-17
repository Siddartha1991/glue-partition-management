#!/bin/bash

NOTIFY_BODY="{
  \"@context\": \"http://schema.org/extensions\",
  \"@type\": \"MessageCard\",
  \"themeColor\": \"#ff0000\",
  \"title\": \"You Broke The Build!\",
  \"text\": \"The build failed after that last merge in ***$CIRCLE_PROJECT_REPONAME*** at job ***$CIRCLE_JOB*** -\
   go to CircleCI! Build is **[here]($CIRCLE_BUILD_URL)** \"
}"

echo "$NOTIFY_BODY"
echo "$GLUECATALOG_WEBHOOK"

curl -H "Content-Type: application/json" -d "$NOTIFY_BODY" "$GLUECATALOG_WEBHOOK"
