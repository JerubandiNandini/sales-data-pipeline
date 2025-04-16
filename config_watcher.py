import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yaml
import logging
import os
import structlog

class ConfigWatcher(FileSystemEventHandler):
    def __init__(self, config, reload_callback):
        self.config = config
        self.reload_callback = reload_callback
        self.logger = logging.getLogger(__name__)
        self.running_tasks = []

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('config.yaml'):
            self.logger.info("Detected config.yaml change, reloading")
            try:
                new_config = self.reload_callback()
                self.config.update(new_config)
                if self.config['logging']['hot_reload']:
                    structlog.configure(
                        processors=[
                            structlog.processors.TimeStamper(fmt="iso"),
                            structlog.stdlib.add_log_level,
                            structlog.processors.JSONRenderer()
                        ],
                        context_class=dict,
                        logger_factory=structlog.stdlib.LoggerFactory(),
                        wrapper_class=structlog.stdlib.BoundLogger,
                        cache_logger_on_first_use=True,
                    )
                self.logger.info("Configuration reloaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to reload config: {str(e)}")

    def start(self):
        observer = Observer()
        observer.schedule(self, path='.', recursive=False)
        observer.start()
        self.logger.info("Started config watcher")