# HRIS Analyzer

A Django web application that accepts an HRIS CSV file, validates employee records, analyzes reporting relationships, detects reporting cycles, and presents the results in a browser-friendly interface.

## Features

The application provides the following six required outputs:

1. **Total source rows**
2. **Accepted employees**
3. **Row-level validation errors with source row numbers**
4. **Root employees with no manager**
5. **Managers and their direct-report counts**
6. **Employees participating in reporting cycles**

The UI presents the results in collapsible sections so that large datasets remain easy to navigate.

---

## Setup and Run Instructions

### Requirements

- Python 3.10+
- Django
- Git (optional)

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv venv
venv\\Scripts\\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser and upload an HRIS CSV.

---
## Screen Recording

The submission contains **two videos** because the free Loom tier used for recording limited individual recordings to approximately 5 minutes and did not provide the required download option.

The two recordings together are approximately **9 minutes** and cover the required code explanation, demonstration, testing, trade-offs, and AI-tool usage.

### 1. HRIS — Code Walkthrough

**Duration:** ~5 minutes

[Watch the Code Walkthrough](https://www.loom.com/share/58f1c41d62f544c2978f23ffc828cda6)

This video covers the key source files and traces the application from CSV upload through parsing, validation, hierarchy analysis, cycle detection, and result display.

### 2. HRIS — Demo, AI Use, Trade-Off and Testing

**Duration:** ~4 minutes

[Watch the Demo, AI Use, Trade-Off and Testing](https://www.loom.com/share/e4fac60123c549a599756cc0efc4673d)

This video covers the working application, testing, edge cases, trade-offs, and AI-tool usage.

Together, the two videos are approximately **9 minutes**. They are provided as two recordings solely because of the Loom free-tier recording limitation described above.

---
## Expected CSV Structure

The analyzer expects an HRIS CSV containing fields including:

```text
employee_id
employee_name
email
manager_id
manager_email
```

Manager relationships may be represented using either `manager_id`, `manager_email`, or both.

---

## Test Instructions

### Supplied sample

1. Start the Django server:
   ```bash
   python manage.py runserver
   ```
2. Open `http://127.0.0.1:8000/`.
3. Select `sample_hris.csv`.
4. Click **Analyze CSV**.
5. Verify the source row count, accepted employees, validation errors, root employees, managers/direct-report counts, and reporting cycles.

### Edge-case testing

During development, Antigravity was used to generate and run **50,000+ test examples**. Testing covered:

- duplicate employee IDs;
- duplicate email addresses;
- missing employee IDs;
- missing email addresses;
- missing managers;
- manager specified by employee ID;
- manager specified by email;
- both manager ID and manager email supplied;
- inconsistent manager ID/email pairs;
- self-reporting employees;
- unknown managers;
- multiple root employees;
- nested reporting structures;
- reporting cycles;
- larger and unusual input structures.

These tests were used to verify validation, hierarchy construction, manager detection, and cycle detection.

---

## Implementation Overview

### CSV Parsing

`parse_csv()` reads the uploaded CSV with `csv.DictReader` and converts rows into dictionaries.

### Normalization

`normalize_rows()` strips surrounding whitespace and converts email addresses to lowercase for consistent comparison.

### Employee Validation

`validate_employees()` checks required fields and duplicate employee IDs/emails. Invalid records are separated from accepted records, while validation errors retain their source row numbers.

### Manager Validation

`manager_validation()` resolves relationships using manager ID and/or manager email. It also identifies root employees and rejects unknown managers, self-management, and inconsistent manager ID/email combinations.

### Hierarchy Construction

`build_hierarchy()` creates an adjacency-list representation:

```text
manager_id -> [direct_report_id, direct_report_id, ...]
```

### Direct-Report Counting

`count_direct_reports()` calculates immediate children for each employee. `get_managers()` identifies employees with at least one direct report.

### Reporting-Cycle Detection

`find_cycles()` uses depth-first search (DFS). `path_index` tracks employees in the active DFS path. If DFS encounters an employee already in that path, a reporting cycle has been found.

`visited` prevents unnecessary traversal of already explored employees. A set-based cycle key prevents duplicate cycle reports.

### Output Construction

`build_output()` assembles the final analysis into one dictionary containing the required outputs, which Django then renders in the browser.

---

## Data Structures and Algorithms

The implementation primarily uses dictionaries, lists, and sets.

**Dictionaries** provide fast employee lookup through structures such as `employees_by_id`, `employees_by_email`, `children`, and `manager_of`.

**Adjacency lists** represent reporting relationships and make graph traversal straightforward.

**DFS cycle detection** distinguishes between globally visited employees and employees currently in the recursion path. Encountering an employee already in the current path indicates a directed cycle.

---

## Assumptions

- `employee_id` uniquely identifies an employee.
- Email addresses are case-insensitive.
- Empty `manager_id` and `manager_email` mean the employee has no manager.
- If both manager ID and manager email are supplied, they must resolve to the same employee.
- Self-referencing manager relationships are invalid.
- Unresolvable managers are invalid.
- Source row numbering starts at 2 because row 1 is the CSV header.
- The uploaded file is expected to be a CSV.
- Core analysis does not require persistent employee records in the database.

---

## Known Limitations

- The application is intended for local/development use and is not configured as a production deployment.
- Uploaded files are temporarily stored during analysis and deleted afterward.
- There is no authentication or authorization layer.
- The UI focuses on analysis rather than persistent HRIS management.
- Very large CSVs may require additional memory optimization because rows are loaded into memory.
- Validation covers the exercise requirements rather than every possible HRIS data-quality rule.
- Cycles are reported as employee IDs rather than visualized as a graph.
- The frontend is intentionally lightweight rather than a full production HR dashboard.

---

## Development Time

Approximately **1 hour 15 minutes**, from around **6:30 PM to 7:45 PM**.

---

## AI Tool Usage

AI tools were used as development aids, while the core logic and application integration were implemented and understood by me.

### ChatGPT

ChatGPT was used as a pair programmer for:

- discussing implementation approaches;
- developing and refining the core logic;
- debugging and integration;
- Django integration guidance;
- generating the frontend HTML and CSS.

The **core analysis logic and application integration were implemented by me**.

The frontend HTML and CSS were generated using ChatGPT; none of the frontend implementation was written manually by me.

### Antigravity

Antigravity was used primarily for testing. It was used to generate and run **50,000+ test examples** to stress-test the implementation and explore edge cases.

### AI-assisted decisions

One example of AI-assisted iteration was using ChatGPT to help structure the Django integration and result presentation. The generated approach was tested against the actual application and changed when it did not match the required deliverables.

AI was therefore used as a development and testing aid rather than as a replacement for understanding the implementation.

---

## Project Structure

```text
HRIS Diversio/
│
├── analyzer/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── templates/
│   └── analyzer/
│       └── upload.html
│
├── main.py
├── manage.py
├── sample_hris.csv
├── README.md
└── db.sqlite3
```

---

## Summary

The project separates HRIS analysis into clear stages: parsing, normalization, validation, manager resolution, hierarchy construction, manager counting, cycle detection, and output formatting.

Django provides the browser-based upload and presentation layer while the core Python analysis remains independent of the web interface.
