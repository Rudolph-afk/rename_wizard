import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"  # Use the synchronous worker class for compatibility with Apache
threads = 32  # Adjust the number of threads as needed
preload = True  # Preload the application to improve performance
timeout = 600

bind = "unix:/var/www/airu/rename/rename.sock"  # IP address and port Gunicorn should bind to. (Using sockets in this case)

# Logging (customize paths and settings as needed or '-' to log to stdout)
accesslog = "-"
errorlog = "-"
