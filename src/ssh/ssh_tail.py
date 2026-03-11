import re

import paramiko
from PyQt6.QtCore import QThread, pyqtSignal
import time


class SSHTailThread(QThread):
    """Thread to tail a remote file via SSH"""

    new_content = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent, host, username, password, remote_file, port=22):
        super().__init__()
        self.host = host
        self.username = username
        self.password = password
        self.remote_file = remote_file
        self.port = port
        self.running = False
        self.ssh_client = None
        self.channel = None
        self.parent = parent

    def sftp(self):
        """Get file content from remote host"""
        try:
            sftp_client = paramiko.SSHClient()
            sftp_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sftp_client.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10,
            )

            sftp = sftp_client.open_sftp()
            with sftp.open(self.remote_file, "r") as f:
                data = f.read().decode("utf-8")
                return data

            # Close connections
            sftp.close()
            sftp_client.close()

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if sftp_client:
                sftp_client.close()

    def run(self):
        """Run SSH tail in background"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10,
            )

            self.channel = self.ssh_client.invoke_shell()
            self.channel.send(f"tail -f {self.remote_file}\n")

            self.running = True
            tail_started = False

            ANSI_ESCAPE = re.compile(r'\x1b\[[^a-zA-Z]*[a-zA-Z]|\[\?2004[hl]')

            while self.running:
                if self.channel.recv_ready():
                    data = self.channel.recv(4096).decode("utf-8", errors="replace")
                    data = ANSI_ESCAPE.sub("", data)
                    
                    if not tail_started:
                        if f"tail -f {self.remote_file}" in data:
                            _, _, data = data.partition(self.remote_file)
                            data = data.split("\n", 1)[-1]
                            tail_started = True
                            # continue
                        else:
                            continue
                    
                    if data.strip():
                        self.new_content.emit(data)
                else:
                    time.sleep(0.1)

            # Close channel
            if self.channel:
                self.channel.send("\x03")  # Ctrl+C
                time.sleep(0.1)
                self.channel.close()

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.ssh_client:
                self.ssh_client.close()

    def stop(self):
        """Stop tailing"""
        self.running = False
        self.parent.ssh_stop.setEnabled(False)
        # End tail command
        if self.channel and not self.channel.closed:
            try:
                self.channel.send("\x03")  # Ctrl+C
                time.sleep(0.2)
            except:
                pass

        # Wait for thread termination
        self.wait(2000)

        # Force close
        if self.isRunning():
            self.terminate()
