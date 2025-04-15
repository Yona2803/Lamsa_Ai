import socket
import threading
import time

class ConnectionMonitor:
    """
    A class that monitors internet connectivity in the background.
    """
    def __init__(self, check_interval=1):
        """
        Initialize the connection monitor.
        
        Args:
            check_interval: Time in seconds between connection checks
        """
        self.check_interval = check_interval
        self._stop_event = threading.Event()
        self._monitor_thread = None
        self.is_connected = False
    
    def _check_connection(self, host="8.8.8.8", port=53, timeout=1):
        """
        Attempts to connect to a DNS server (default: Google DNS).
        Returns True if successful, False otherwise.
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            return False
    
    def _monitor_connection(self):
        """Background thread that continuously checks connection"""
        while not self._stop_event.is_set():
            # Update connection status
            self.is_connected = self._check_connection()
            
            # Wait before checking again
            self._stop_event.wait(self.check_interval)
    
    def start(self):
        """Start monitoring the internet connection"""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._stop_event.clear()
            self._monitor_thread = threading.Thread(target=self._monitor_connection, daemon=True)
            self._monitor_thread.start()
            return True
        return False
    
    def stop(self):
        """Stop monitoring the internet connection"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_event.set()
            self._monitor_thread.join(timeout=1.0)
            self._monitor_thread = None
            return True
        return False