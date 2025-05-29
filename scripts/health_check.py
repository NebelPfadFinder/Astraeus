[supervisord]
# Supervisor main configuration for Chatbot Application
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid
childlogdir=/var/log/supervisor
user=root
silent=false
minfds=1024
minprocs=200

[unix_http_server]
file=/var/run/supervisor.sock
chmod=0700

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock

# Streamlit Application
[program:streamlit]
command=streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
directory=/app
user=app
autostart=true
autorestart=true
