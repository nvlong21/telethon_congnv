import subprocess
subprocess.Popen(["python", "service_crawl.py"])
subprocess.Popen(["python", "service_sender.py"])
subprocess.run(["python", "app.py"])