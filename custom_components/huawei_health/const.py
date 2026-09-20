from datetime import timedelta
DOMAIN="huawei_health"
PLATFORMS=["calendar","sensor"]
DEFAULT_NAME="Huawei Health"; DEFAULT_REGION="eu"; DEFAULT_SCAN_INTERVAL=timedelta(minutes=30); DEFAULT_HISTORY_DAYS=30
CONF_REGION="region"; CONF_REDIRECT_URI="redirect_uri"; CONF_ACCESS_TOKEN="access_token"; CONF_REFRESH_TOKEN="refresh_token"; CONF_EXPIRES_AT="expires_at"
CONF_ENABLE_ACTIVITIES="enable_activities";
# CONF_ENABLE_SLEEP="enable_sleep";
CONF_ENABLE_SLEEP= False;
CONF_ENABLE_NAPS="enable_naps";
CONF_HISTORY_DAYS="history_days"
REGION_API_BASE={"eu":"https://health-api.cloud.huawei.com/healthkit/v2"}
OAUTH_AUTHORIZE_URL="https://oauth-login.cloud.huawei.com/oauth2/v3/authorize"; OAUTH_TOKEN_URL="https://oauth-login.cloud.huawei.com/oauth2/v3/token"
ACTIVITY_PATH="activityRecords"; HEALTH_RECORD_PATH="healthRecords"; SLEEP_DATA_TYPE="com.huawei.health.record.sleep"
SLEEP_SCOPE="https://www.huawei.com/healthkit/sleep.read"
# The activity scope granted in Huawei Developers must be inserted here if its value differs for your product.
ACTIVITY_SCOPE="https://www.huawei.com/healthkit/activity.read"
