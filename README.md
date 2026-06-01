# 💉 Code Injection Security Lab

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20Dashboard-green)
![AppSec](https://img.shields.io/badge/Application-Security-red)
![OWASP](https://img.shields.io/badge/OWASP-Education-orange)
![Status](https://img.shields.io/badge/Status-Educational-success)

## Interactive Code Injection & Secure Coding Learning Platform

Code Injection Security Lab is an educational cybersecurity project developed by **Karanam Shrivasta**.

The project demonstrates multiple code injection vulnerabilities and their secure counterparts through interactive simulations. Users can explore how attackers exploit insecure code and learn defensive programming techniques using side-by-side comparisons. :contentReference[oaicite:0]{index=0}

---

# ✨ Features

## Injection Demonstrations

- Eval Injection
- Exec Injection
- Command Injection
- Format String Injection
- Server-Side Template Injection (SSTI)
- Pickle Deserialization Injection

## Secure Coding Demonstrations

- Input Validation
- Whitelist Filtering
- Safe Deserialization
- AST-Based Validation
- Template Restrictions
- Secure Command Execution

## Learning Features

- Interactive Payload Library
- Vulnerable vs Secure Comparisons
- Attack Explanations
- Security Recommendations
- Educational Walkthroughs
- Sandbox Demonstrations

## Dashboard Features

- Modern Flask Dashboard
- Mobile Friendly Interface
- Dark Theme
- Light Theme
- Interactive Navigation
- Real-Time Testing

---

# ⚙️ How It Works

Code Injection Security Lab contains vulnerable and secure implementations of common programming mistakes.

Workflow:

1. User selects an injection category.
2. User enters a payload.
3. Vulnerable mode processes the payload.
4. The vulnerability impact is demonstrated.
5. Secure mode processes the same payload.
6. Security controls block or mitigate the attack.
7. Educational explanations are displayed.

The goal is to teach both offensive and defensive application security concepts.

---

# 🏗️ Architecture

```text
User
 │
 ▼
Web Dashboard
 │
 ├── Eval Injection Module
 ├── Exec Injection Module
 ├── Command Injection Module
 ├── Format String Module
 ├── SSTI Module
 └── Pickle Module
 │
 ▼
Vulnerable Mode
 │
 ▼
Attack Simulation
 │
 ▼
Secure Mode
 │
 ▼
Mitigation Demonstration
 │
 ▼
Learning Dashboard
```

---

# 🔬 Injection Types Covered

## Eval Injection

Demonstrates risks of:

```python
eval(user_input)
```

Topics:

- Arbitrary Code Execution
- Python Imports
- File Access Risks
- Unsafe Evaluation

---

## Exec Injection

Demonstrates risks of:

```python
exec(user_code)
```

Topics:

- Arbitrary Script Execution
- Dangerous Imports
- Runtime Manipulation
- Secure AST Validation

---

## Command Injection

Demonstrates:

```python
os.system(user_input)
```

Topics:

- Shell Injection
- Command Chaining
- Path Traversal
- Secure Input Validation

---

## Format String Injection

Demonstrates:

```python
template.format(**config)
```

Topics:

- Secret Disclosure
- Internal Variable Leakage
- Safe Variable Restriction

---

## SSTI

Topics:

- Template Exploitation
- Python Introspection
- Object Traversal
- Template Restrictions

---

## Pickle Injection

Topics:

- Insecure Deserialization
- Remote Code Execution Concepts
- Safe JSON Alternatives

---

# 📦 Installation

## Clone Repository

```bash
git clone https://github.com/mrshrivasta/Code-Injection-Security-Lab.git

cd Code-Injection-Security-Lab
```

## Install Requirements

```bash
pip install flask
```

## Run Application

```bash
python code_injection_demo.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# 🚀 Usage

### Step 1

Launch the application.

### Step 2

Open the dashboard.

### Step 3

Select an injection category.

### Step 4

Choose:

```text
❌ Vulnerable Mode
```

or

```text
✅ Secure Mode
```

### Step 5

Run sample payloads.

### Step 6

Compare results and learn mitigation techniques.

---

# 🎯 Educational Objectives

This project helps users learn:

- Application Security
- Secure Coding
- OWASP Concepts
- Injection Prevention
- Input Validation
- Secure Deserialization
- Secure Template Handling
- Safe Command Execution
- Defensive Programming

---

# 📱 Dashboard Modules

```text
🏠 Overview

🧮 Eval Injection

⚡ Exec Injection

💻 Command Injection

📝 Format String Injection

🥒 Pickle Injection

🌐 SSTI

📚 Learning Center
```

---

# 📊 Vulnerable vs Secure Comparison

| Vulnerability | Vulnerable Implementation | Secure Implementation |
|--------------|---------------------------|----------------------|
| Eval | Direct eval() | Input Validation |
| Exec | Direct exec() | AST Validation |
| Command | String Concatenation | Whitelist Validation |
| SSTI | User Templates | Restricted Templates |
| Pickle | pickle.loads() | JSON Parsing |
| Format String | Internal Variables Exposed | Safe Variables Only |

---

# ❓ FAQ

### Does this perform real attacks?

No.

All demonstrations run in a controlled educational environment.

### Is this malware?

No.

### Does this attack external systems?

No.

### Is this safe for learning?

Yes.

The project is specifically designed for cybersecurity education.

### Can it be used for production security testing?

No.

This is a learning platform.

---

# 🛣️ Roadmap

- [ ] SQL Injection Module
- [ ] XSS Demonstration Module
- [ ] CSRF Demonstration Module
- [ ] XXE Demonstration Module
- [ ] SSRF Demonstration Module
- [ ] Docker Support
- [ ] Multi-User Labs
- [ ] Security Challenges
- [ ] Interactive Tutorials

---

# 🔍 SEO Keywords

```text
Code Injection Security Lab
Karanam Shrivasta
Code Injection
Eval Injection
Exec Injection
Command Injection
SSTI
Pickle Deserialization
Format String Injection
Application Security
OWASP
Secure Coding
Cybersecurity Education
Flask Security Project
AppSec
Defensive Security
Python Security
Security Research
Input Validation
Security Learning
```

---

# ⚠️ IMPORTANT DISCLAIMER

## READ BEFORE USING THIS SOFTWARE

Code Injection Security Lab is an educational cybersecurity project created by **Karanam Shrivasta**.

This project is provided strictly for:

- Educational Purposes
- Research Purposes
- Learning Purposes
- Demonstration Purposes
- Security Awareness
- Portfolio Purposes

This project is NOT:

- A Hacking Tool
- A Malware Framework
- A Commercial Security Product
- A Penetration Testing Platform
- A Production Security Solution

---

# ⚠️ SANDBOX NOTICE

All demonstrations are intentionally designed to operate in a local educational sandbox.

The project does not perform real attacks against external systems.

Users must not attempt to apply demonstrated techniques against systems without explicit authorization.

---

# ⚠️ NO WARRANTY

THIS SOFTWARE IS PROVIDED "AS IS".

NO WARRANTIES OF ANY KIND ARE PROVIDED.

The author makes NO guarantee regarding:

- Accuracy
- Reliability
- Security Findings
- Educational Results
- Software Stability
- Vulnerability Coverage
- Learning Outcomes

The software may contain:

- Bugs
- Errors
- Incomplete Simulations
- False Assumptions
- Educational Simplifications

---

# ⚠️ USER RESPONSIBILITY

By downloading, installing, modifying, distributing, or using this software, you acknowledge and agree that:

- You are solely responsible for your actions.
- You are solely responsible for how you use this software.
- You are solely responsible for compliance with applicable laws.
- You are solely responsible for any modifications made to the software.

USE THIS SOFTWARE ENTIRELY AT YOUR OWN RISK.

---

# ⚠️ LIABILITY DISCLAIMER

To the maximum extent permitted by law:

**Karanam Shrivasta shall not be responsible or liable for:**

- Misuse of the Software
- Security Incidents
- Data Loss
- System Failures
- Legal Consequences
- Financial Losses
- Business Losses
- Direct Damages
- Indirect Damages
- Consequential Damages
- Special Damages

Once this software has been downloaded, installed, modified, distributed, or used, all responsibility remains solely with the user.

---

# ⚠️ AUTHORIZATION NOTICE

Users must only perform testing, research, experimentation, or demonstrations on systems they own or are explicitly authorized to access.

Unauthorized testing may violate laws and regulations.

The author does not authorize or endorse unlawful activity.

---

# 👨‍💻 Author

## Karanam Shrivasta

Cybersecurity Enthusiast • Application Security Learner • Developer

GitHub:
https://github.com/mrshrivasta

LinkedIn:
https://linkedin.com/in/karanam-shrivasta

---

# 📜 License

Educational and Research Use Only.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

USE AT YOUR OWN RISK.

© Karanam Shrivasta. All Rights Reserved.
