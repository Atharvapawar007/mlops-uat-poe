# MLOps / DevOps Internal POE: Complete Windows UAT Dry Run & Setup Manual

This manual walks you through every step required for your Internal POE (Proof of Execution) as a DevOps/MLOps Engineer configuring a UAT (User Acceptance Testing) environment on **Windows 10/11**. Every command, file, configuration setting, and troubleshooting fix is included so you can execute the dry run smoothly without last-minute surprises.

## Pre-Flight Checklist: System Requirements on Windows

Before starting the 12 steps, verify these three prerequisites on your Windows machine:

1. **Administrator Privileges**: You need local Administrator rights to install Docker Desktop, Java (JDK), and Jenkins.
2. **Hardware Virtualization Enabled**: Open **Task Manager** (`Ctrl + Shift + Esc`) → **Performance** tab → **CPU**. Verify that **Virtualization: Enabled** is shown at the bottom right (required for Docker Desktop and WSL 2).
3. **Python 3.10 or 3.11 Installed**:
   - Download from [python.org/downloads/windows](https://www.google.com/search?q=https://www.python.org/downloads/windows/).
   - **Critical Gotcha**: During installation, check the box **"Add python.exe to PATH"** on the very first screen before clicking Install.
   - Verify in PowerShell or Command Prompt:
     ```powershell
     python --version
     pip --version
     ```

## Step 1: Form a Team of Two Developers (As per Timetable)

Coordinate with your lab partner from the same practical batch as per your college timetable:

1. **Developer 1 (Host / Primary System)**: Sets up the local UAT environment (VS Code, Git, Jenkins, Docker, Pytest, Evidently) and creates the GitHub repository.
2. **Developer 2 (Collaborator / Reviewer)**: Can be added as a collaborator on the GitHub repository (**Settings → Collaborators → Add people**) and co-authors the Dry Run Summary Report.
3. Keep both Roll Numbers, Names, Batch ID, and GitHub usernames documented at the top of your `README.md` and Summary Report.

## Step 2 & Step 3: Create the VS Code Project & Single-File Application (`hello.py`)

### 3.1 Install Visual Studio Code
1. Download VS Code from [code.visualstudio.com](https://www.google.com/search?q=https://code.visualstudio.com/) and install it.
2. During installation, check **"Add 'Open with Code' action to Windows Explorer directory context menu"** and **"Add to PATH"**.

### 3.2 Create the Project Directory & Virtual Environment
Open **PowerShell** and run the following commands to create a clean project folder and an isolated Python virtual environment:

```powershell
mkdir C:\mlops-uat-poe
cd C:\mlops-uat-poe
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> **Windows PowerShell Execution Policy Gotcha**: If `.\venv\Scripts\Activate.ps1` gives a red error saying *"running scripts is disabled on this system"*, run this command first in the same PowerShell window and type `Y` when prompted:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then run `.\venv\Scripts\Activate.ps1` again. You will see `(venv)` at the start of your prompt.

### 3.3 Open the Project in VS Code
```powershell
code .
```

### 3.4 Create `hello.py` (Step 2)
In VS Code, create a new file named `hello.py` in the root of `C:\mlops-uat-poe` with the following code. Writing it with a helper function makes Step 11 (`pytest`) seamless:

```python
# hello.py

def get_greeting(environment: str = "UAT") -> str:
    """Return a status greeting for the target environment."""
    return f"Hello from MLOps {environment} Environment! Dry Run Successful."


def add_metrics(a: int, b: int) -> int:
    """Simple helper function for pytest verification."""
    return a + b


if __name__ == "__main__":
    print(get_greeting("UAT"))
    print(f"Health Check Calculation (2 + 3): {add_metrics(2, 3)}")
```

Test it immediately in the VS Code terminal (`Ctrl + ~`):
```powershell
python hello.py
```
**Expected Output**:
```text
Hello from MLOps UAT Environment! Dry Run Successful.
Health Check Calculation (2 + 3): 5
```

### 3.5 Create Project Supporting Files Now (Recommended)
To keep your repository complete when Jenkins pulls from GitHub in Step 6, create these additional files inside `C:\mlops-uat-poe` right now (or push an update after creating them in Steps 10–12):

- **`.gitignore`** (Crucial so you do NOT upload the heavy `venv` folder to GitHub):
  ```text
  venv/
  __pycache__/
  .pytest_cache/
  *.pyc
  ```

- **`requirements.txt`**:
  ```text
  pytest==8.3.3
  evidently==0.4.33
  pandas==2.2.3
  scikit-learn==1.5.2
  ```

## Step 4: Push Project Structure to Git & GitHub

### 4.1 Install Git for Windows
1. Download Git from [git-scm.com/download/win](https://www.google.com/search?q=https://git-scm.com/download/win) and install with default options.
2. Verify installation in PowerShell:
   ```powershell
   git --version
   ```

### 4.2 Create a New Public Repository on GitHub
1. Log in to [github.com](https://www.google.com/url?sa=E&source=gmail&q=https://github.com/) and click the **+** icon (top right) → **New repository**.
2. Set **Repository name**: `mlops-uat-poe`
3. Set visibility to **Public** (this avoids complex credential token errors when Jenkins pulls your code in Step 6!).
4. Leave **"Add a README file"** unchecked (since you already have a local project).
5. Click **Create repository** and copy the HTTPS URL (e.g., `https://github.com/<your-username>/mlops-uat-poe.git`).

### 4.3 Initialize Git, Commit, and Push from Windows
Run these commands inside `C:\mlops-uat-poe`:

```powershell
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
git add .
git commit -m "Initial commit: Add hello.py and UAT project structure"
git branch -M main
git remote add origin https://github.com/<your-username>/mlops-uat-poe.git
git push -u origin main
```

> **GitHub Authentication Gotcha**: When `git push` runs for the first time on Windows, a **Git Credential Manager** pop-up window will appear asking you to **"Sign in with your browser"**. Click that button and authorize in your browser. Do **not** type your standard GitHub account password into the terminal—GitHub requires browser OAuth or a Personal Access Token (PAT).

## Step 5, Step 6 & Step 7: Install, Configure & Run Jenkins, and Pull Code from GitHub

### 5.1 Install Java JDK 17 or JDK 21 (Required by Jenkins)
Jenkins will **fail to install or start** without a supported Java JDK (JDK 17 or JDK 21).
1. Download **Eclipse Temurin JDK 17 (x64 MSI)** from [adoptium.net](https://www.google.com/search?q=https://adoptium.net/) or install via Windows Package Manager (`winget`) in PowerShell (Admin):
   ```powershell
   winget install EclipseAdoptium.Temurin.17.JDK
   ```
2. Close and reopen PowerShell, then verify Java is installed and get its exact path:
   ```powershell
   java -version
   where.exe java
   ```
   *(Typical install path: `C:\Program Files\Eclipse Adoptium\jdk-17.0.x.x-hotspot\bin\java.exe`)*

### 5.2 Download and Install Jenkins on Windows (Step 5)
1. Download the **Windows MSI Installer (LTS version)** from [jenkins.io/download](https://www.google.com/search?q=https://www.jenkins.io/download/).
2. Double-click `jenkins.msi` to start the setup wizard:
   - **Destination Folder**: Keep default (`C:\Program Files\Jenkins`).
   - **Service Logon Credentials**: Select **"Run service as LocalSystem (not recommended)"** for a local college lab UAT dry run. Why? The default "Local Service" account often lacks permissions to run Python, Git, or Docker commands on Windows without complex ACL configuration.
   - **Port Selection**: Enter `8080` and click **Test Port** (if port 8080 is busy, change it to `8081` and click **Test Port** until a green checkmark appears).
   - **Select Java Home Directory**: Browse and select your JDK 17 folder (e.g., `C:\Program Files\Eclipse Adoptium\jdk-17.0.x.x-hotspot`).
   - Click **Install** and **Finish**.

### 5.3 Unlock and Configure Jenkins (Step 5 & Step 7)
1. Open your browser and navigate to `http://localhost:8080` (or `http://localhost:8081`).
2. **Unlock Jenkins**:
   - Open PowerShell as Administrator and read the initial admin password:
     ```powershell
     Get-Content "C:\ProgramData\Jenkins\.jenkins\secrets\initialAdminPassword"
     ```
   - *(Note: `C:\ProgramData` is a hidden folder in Windows Explorer; using the `Get-Content` command above copies it cleanly without searching hidden folders.)*
   - Paste the password into the Jenkins web screen and click **Continue**.
3. Click **Install suggested plugins** (wait 2–4 minutes for plugins like Git and Pipeline to install).
4. **Create First Admin User**:
   - Username: `admin`
   - Password: `admin123` (or a password you won't forget during your lab exam)
   - Click **Save and Continue** → **Save and Finish** → **Start using Jenkins**.

### 5.4 Pull Code from GitHub & Run a Jenkins Job (Step 6 & Step 7)
1. On the Jenkins Dashboard, click **+ New Item** (top left).
2. Enter item name: `MLOps-UAT-DryRun`
3. Select **Freestyle project** and click **OK**.
4. Under **Source Code Management**:
   - Select **Git**.
   - **Repository URL**: Paste your GitHub URL (`https://github.com/<your-username>/mlops-uat-poe.git`).
   - **Branches to build**: Change `*/master` to `*/main` (Crucial Gotcha! GitHub uses `main` by default, whereas Jenkins defaults to `*/master`. If you leave `*/master`, the build will fail with `ERROR: Couldn't find any revision to build`).
5. Under **Build Steps**:
   - Click **Add build step** → **Execute Windows batch command** (Important: choose **Execute Windows batch command**, NOT "Execute shell", because "Execute shell" tries to call Linux `/bin/sh` and fails on Windows).
   - Enter the following commands in the command box:
     ```bat
     echo "=== Starting UAT Dry Run in Jenkins ==="
     python --version
     python hello.py
     ```
6. Click **Save**.
7. On the project page, click **Build Now** on the left sidebar.
8. Click the build number (`#1`) under **Build History** → **Console Output**.
9. Verify you see:
   ```text
   Hello from MLOps UAT Environment! Dry Run Successful.
   Finished: SUCCESS
   ```
   *(Take a screenshot of this Console Output for your POE submission!)*

## Step 8, Step 9 & Step 10: Install Docker, Pull Python Image & Containerize `hello.py`

### 8.1 Install WSL 2 and Docker Desktop on Windows (Step 8)
1. Open **PowerShell as Administrator** and run:
   ```powershell
   wsl --install
   ```
   *(If WSL is wasn't previously enabled, restart your computer when prompted.)*
2. Download **Docker Desktop for Windows** from [docker.com/products/docker-desktop](https://www.google.com/search?q=https://www.docker.com/products/docker-desktop/).
3. Run `Docker Desktop Installer.exe`. Keep **"Use WSL 2 instead of Hyper-V (recommended)"** checked.
4. Once installed, launch **Docker Desktop** from the Start Menu and wait until the bottom-left whale icon turns green (**Engine running**).
5. Verify Docker in PowerShell:
   ```powershell
   docker --version
   docker info
   ```

### 8.2 Pull Lightweight Python Docker Image (Step 9)
In PowerShell, pull the official lightweight `python:3.11-slim` image (around ~45 MB compressed vs ~1 GB for the full image):

```powershell
docker pull python:3.11-slim
docker images
```
*(Take a screenshot of `docker images` showing `python` with tag `3.11-slim`.)*

### 8.3 Add `hello.py` to Docker via `Dockerfile` (Step 10)
1. In your VS Code project folder (`C:\mlops-uat-poe`), create a file named `Dockerfile` (exact capitalization, **no `.txt` extension**).
   > **Windows File Extension Gotcha**: Make sure Windows Explorer or VS Code does not name it `Dockerfile.txt`. In VS Code, creating a file named `Dockerfile` directly in the Explorer sidebar automatically shows the blue Docker whale icon.

2. Add the following lines to `Dockerfile`:
   ```dockerfile
   # Use lightweight official Python image
   FROM python:3.11-slim

   # Set working directory inside the container
   WORKDIR /app

   # Copy application and test files into the container
   COPY hello.py /app/hello.py

   # Command to execute when the container starts
   CMD ["python", "hello.py"]
   ```

3. Build the Docker image and run the container in PowerShell:
   ```powershell
   docker build -t mlops-hello-uat:v1 .
   docker run --rm mlops-hello-uat:v1
   ```
   *(Note: Don't forget the trailing dot `.` at the end of `docker build -t mlops-hello-uat:v1 .`!)*

4. **Expected Output**:
   ```text
   Hello from MLOps UAT Environment! Dry Run Successful.
   Health Check Calculation (2 + 3): 5
   ```
   *(Take a screenshot of the `docker build` and `docker run` output!)*

## Step 11: Configure `pytest` and Print 1 Test Case

### 11.1 Install `pytest`
Make sure your virtual environment `(venv)` is active in `C:\mlops-uat-poe`, then install `pytest`:

```powershell
pip install pytest
pytest --version
```

### 11.2 Create `test_hello.py`
In VS Code (`C:\mlops-uat-poe`), create a file named `test_hello.py`:

```python
# test_hello.py
from hello import get_greeting, add_metrics


def test_uat_greeting():
    """Test Case 1: Verify UAT greeting message and metric calculation."""
    greeting = get_greeting("UAT")
    print(f"\n[PYTEST LOG] Printed Output -> {greeting}")
    assert "Hello from MLOps UAT Environment!" in greeting
    assert add_metrics(2, 3) == 5
```

### 11.3 Run `pytest` and Print the Test Case Output
Run `pytest` with the `-v` (verbose) and `-s` (capture=no, which prints `print()` statements inside tests to the terminal):

```powershell
pytest -v -s
```

**Expected Output**:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.x, pytest-8.x.x, pluggy-1.x.x
collected 1 item

test_hello.py::test_uat_greeting
[PYTEST LOG] Printed Output -> Hello from MLOps UAT Environment! Dry Run Successful.
PASSED

============================== 1 passed in 0.03s ==============================
```

## Step 12: Configure Evidently AI Tool & Monitor

Evidently AI is an open-source MLOps Python library used to evaluate, test, and monitor ML models and data drift between a **Reference dataset** (training/baseline data) and a **Current dataset** (production/UAT data).

### 12.1 Install Evidently AI and Dependencies
Run the following in your activated `(venv)` terminal:

```powershell
pip install evidently pandas scikit-learn
```

### 12.2 Create `monitor.py` for Data Drift Monitoring
In VS Code (`C:\mlops-uat-poe`), create `monitor.py`:

```python
# monitor.py
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset


def run_evidently_monitor():
    # 1. Create Reference Dataset (Baseline / Training Data)
    reference_data = pd.DataFrame({
        "feature_age": [22, 25, 28, 30, 35, 40, 23, 27, 31, 29],
        "feature_salary": [30000, 35000, 42000, 50000, 60000, 65000, 32000, 40000, 52000, 48000],
        "prediction": [0, 0, 1, 1, 1, 1, 0, 0, 1, 1]
    })

    # 2. Create Current Dataset (Simulated UAT / Production Data with slight shift)
    current_data = pd.DataFrame({
        "feature_age": [45, 50, 52, 48, 60, 55, 49, 53, 58, 62],
        "feature_salary": [80000, 85000, 90000, 78000, 95000, 88000, 82000, 91000, 94000, 99000],
        "prediction": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    })

    # 3. Configure Evidently Data Drift Report
    drift_report = Report(metrics=[DataDriftPreset()])
    drift_report.run(reference_data=reference_data, current_data=current_data)

    # 4. Save Interactive HTML Monitoring Dashboard
    output_file = "evidently_uat_monitoring_report.html"
    drift_report.save_html(output_file)
    print(f"[SUCCESS] Evidently Monitoring Report generated: {output_file}")


if __name__ == "__main__":
    run_evidently_monitor()
```

### 12.3 Execute the Monitor & Open the Interactive Dashboard
Run the script in PowerShell:

```powershell
python monitor.py
start evidently_uat_monitoring_report.html
```

- `start evidently_uat_monitoring_report.html` automatically opens the visual Evidently Data Drift dashboard in your Windows web browser.
- **Bonus Option (Live Evidently UI Server)**: If your faculty asks to see the live Evidently UI workspace server running on a port, run:
  ```powershell
  evidently ui --workspace ./evidently_workspace --port 8000
  ```
  and open `http://localhost:8000` in your browser.

### 12.4 Push Final All-In-One Project to GitHub & Re-Run Jenkins
Once all files (`hello.py`, `test_hello.py`, `Dockerfile`, `monitor.py`, `requirements.txt`, `.gitignore`) are created, push them to GitHub so your repository and Jenkins job reflect the entire project:

```powershell
git add .
git commit -m "Complete UAT Dry Run: Add Dockerfile, pytest, and Evidently monitoring"
git push origin main
```

Optionally update your Jenkins **Execute Windows batch command** in Step 5.4 to run the entire suite automatically:
```bat
python hello.py
pytest -v -s
python monitor.py
```

## Final Deliverable: UAT Environment Installation & Dry Run Summary Report

Copy or print the table below for your Internal POE submission sheet. Fill in your names/roll numbers at the top.

### Project & Team Metadata
- **Course / Lab**: MLOps / DevOps Internal POE — UAT Environment Dry Run
- **Operating System**: Windows 10 / 11 (64-bit)
- **Developer 1 (Name & Roll No.)**: ___________________________
- **Developer 2 (Name & Roll No.)**: ___________________________
- **GitHub Repository URL**: `https://github.com/<your-username>/mlops-uat-poe`

### Tool Installation & Execution Summary Table

| Step | Tool / Component Name | Commands Used | Expected Verification Output | Installation / Dry Run Status |
| :--- | :--- | :--- | :--- | :--- |
| **2** | **Python 3.11 & `hello.py`** | `python --version`<br>`python hello.py` | Prints `Python 3.11.x` and `Hello from MLOps UAT Environment! Dry Run Successful.` | **Successful (PASS)** |
| **3** | **Visual Studio Code** | `code --version`<br>`python -m venv venv`<br>`.\venv\Scripts\Activate.ps1` | Opens project workspace in VS Code and activates virtual environment `(venv)` | **Successful (PASS)** |
| **4** | **Git & GitHub** | `git init`<br>`git add .`<br>`git commit -m "Initial commit"`<br>`git branch -M main`<br>`git remote add origin <URL>`<br>`git push -u origin main` | Pushes local project structure (`hello.py`, `Dockerfile`, tests) to remote GitHub `main` branch | **Successful (PASS)** |
| **5** | **Java JDK 17 & Jenkins Installation** | `winget install EclipseAdoptium.Temurin.17.JDK`<br>`java -version`<br>`jenkins.msi` (Service on Port `8080`) | Java 17 verified; Jenkins Web UI unlocked and accessible at `http://localhost:8080` | **Successful (PASS)** |
| **6 & 7** | **Jenkins Git Pull & Pipeline Run** | Jenkins Freestyle Job → Git SCM (`*/main`) → Windows Batch:<br>`python hello.py` | Jenkins clones GitHub repository into workspace and logs `Finished: SUCCESS` in Console Output | **Successful (PASS)** |
| **8** | **WSL 2 & Docker Desktop** | `wsl --install`<br>`docker --version`<br>`docker info` | Docker Engine running on Windows WSL 2 backend without errors | **Successful (PASS)** |
| **9** | **Lightweight Python Docker Image** | `docker pull python:3.11-slim`<br>`docker images` | Pulls official `python:3.11-slim` image and lists it in local Docker image registry | **Successful (PASS)** |
| **10** | **Docker Container (`hello.py`)** | `docker build -t mlops-hello-uat:v1 .`<br>`docker run --rm mlops-hello-uat:v1` | Builds custom container image and outputs greeting from inside the isolated container | **Successful (PASS)** |
| **11** | **Pytest Framework** | `pip install pytest`<br>`pytest -v -s` | Collects 1 test item in `test_hello.py`, prints test log, and reports `1 passed` | **Successful (PASS)** |
| **12** | **Evidently AI Monitoring Tool** | `pip install evidently pandas scikit-learn`<br>`python monitor.py`<br>`start evidently_uat_monitoring_report.html` | Evaluates Data Drift between Reference and Current datasets and opens HTML monitoring report | **Successful (PASS)** |

## Quick Reference: Common Last-Minute Exam Troubleshooting Fixes

| Issue / Error Message | Root Cause on Windows | Instant Fix |
| :--- | :--- | :--- |
| `'python' is not recognized as an internal or external command` | Python was not added to Windows `PATH` during installation | Re-run the Python installer → click **Modify** → check **Add Python to environment variables**, or use `py hello.py`. |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | Default Windows PowerShell execution policy blocks `.ps1` scripts | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell, then retry. |
| Jenkins build fails with `ERROR: Couldn't find any revision to build` | Jenkins defaults to `*/master` while GitHub uses `*/main` | In Jenkins job **Configure → Source Code Management → Branches to build**, change `*/master` to `*/main`. |
| Jenkins build fails with `'sh' is not recognized` | Selected "Execute shell" instead of "Execute Windows batch command" | In Jenkins job **Configure → Build Steps**, delete "Execute shell" and add **Execute Windows batch command**. |
| `docker pull` fails with `error during connect: ... open //./pipe/dockerDesktopLinuxEngine` | Docker Desktop application is closed or still starting up | Open **Docker Desktop** from the Windows Start Menu and wait until the bottom-left bar says **Engine running**. |
| `docker build` fails with `failed to read dockerfile: open Dockerfile: no such file` | Windows Notepad/Explorer saved the file as `Dockerfile.txt` | Run `ren Dockerfile.txt Dockerfile` in PowerShell inside `C:\mlops-uat-poe`. |
