import sys
import csv
import json


def parse_csv(file_path):
    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    return rows


def normalize_rows(rows):
    normalized_rows = []

    for row in rows:
        normalized_row = {}

        for key, value in row.items():
            value = value.strip()

            if key == "email" or key == "manager_email":
                value = value.lower()

            normalized_row[key] = value

        normalized_rows.append(normalized_row)

    return normalized_rows


def num_employees(rows):
    employeeIDs = {}
    emails = {}

    for row in rows:
        if row["employee_id"] not in employeeIDs:
            employeeIDs[row["employee_id"]] = 1
        else:
            employeeIDs[row["employee_id"]] += 1

        if row["email"] not in emails:
            emails[row["email"]] = 1
        else:
            emails[row["email"]] += 1

    return employeeIDs, emails

def validate_employees(rows):

    invalid_rows = []
    accepted_rows = []
    validation_errors = []

    employeeIDs, emails = num_employees(rows)

    invalid_employeeIDs = {
        id for id, count in employeeIDs.items()
        if count > 1
    }

    invalid_emails = {
        email for email, count in emails.items()
        if count > 1
    }

    for row_number, row in enumerate(rows, start=2):

        errors = []

        if not row["employee_id"]:
            errors.append("employee_id is required")

        if not row["email"]:
            errors.append("email is required")

        if row["employee_id"] in invalid_employeeIDs:
            errors.append("duplicate employee_id")

        if row["email"] in invalid_emails:
            errors.append("duplicate email")

        if errors:
            invalid_rows.append(row)

            validation_errors.append({
                "row": row_number,
                "errors": errors
            })
        else:
            accepted_rows.append(row)

    return invalid_rows, accepted_rows, validation_errors


def manager_validation(accepted_rows):
    employees_by_id = {row["employee_id"]: row for row in accepted_rows}
    employees_by_email = {row["email"]: row for row in accepted_rows}
    roots = []
    manager_of = {}
    manager_errors = []
    for row in accepted_rows:
        if not row["manager_id"] and not row["manager_email"]:
            roots.append(row)

        if row["manager_id"] and not row["manager_email"]:
            if row["manager_id"] in employees_by_id:
                if row["employee_id"] == row["manager_id"]:
                    manager_errors.append(row)
                else:
                    manager_of[row["employee_id"]] = row["manager_id"]
            else:
                manager_errors.append(row)

        if row["manager_email"] and not row["manager_id"]:
            if row["manager_email"] in employees_by_email:
                manager = employees_by_email[row["manager_email"]]

                if row["employee_id"] == manager["employee_id"]:
                    manager_errors.append(row)
                else:
                    manager_of[row["employee_id"]] = manager["employee_id"]
            else:
                manager_errors.append(row)

        if row["manager_id"] and row["manager_email"]:
            manager_by_id = employees_by_id.get(row["manager_id"])
            manager_by_email = employees_by_email.get(row["manager_email"])

            if (
                manager_by_id
                and manager_by_email
                and manager_by_id["employee_id"] == manager_by_email["employee_id"]
            ):
                if row["employee_id"] == manager_by_id["employee_id"]:
                    manager_errors.append(row)
                else:
                    manager_of[row["employee_id"]] = manager_by_id["employee_id"]

            else:
                manager_errors.append(row)       

    return roots, manager_of, manager_errors

def build_hierarchy(accepted_rows, manager_of):
    children = {}

    for row in accepted_rows:
        employee_id = row["employee_id"]

        if employee_id not in children:
            children[employee_id] = []

    for employee_id, manager_id in manager_of.items():
        children[manager_id].append(employee_id)

    return children

def count_direct_reports(children):
    direct_reports = {}

    for employee_id, reports in children.items():
        direct_reports[employee_id] = len(reports)

    return direct_reports

def get_managers(accepted_rows, direct_reports):
    managers = []

    employees_by_id = {
        row["employee_id"]: row
        for row in accepted_rows
    }

    for employee_id, count in direct_reports.items():
        if count > 0:
            employee = employees_by_id[employee_id]

            managers.append({
                "employee_id": employee_id,
                "employee_name": employee["employee_name"],
                "direct_reports": count
            })

    return managers

def find_cycles(children):
    cycles = []
    visited = set()
    path = []
    path_index = {}

    def dfs(employee_id):
        if employee_id in path_index:
            start = path_index[employee_id]
            cycle = path[start:].copy()

            # Avoid duplicate cycles
            cycle_key = frozenset(cycle)

            if cycle_key not in {
                frozenset(existing_cycle)
                for existing_cycle in cycles
            }:
                cycles.append(cycle)

            return

        if employee_id in visited:
            return

        visited.add(employee_id)
        path_index[employee_id] = len(path)
        path.append(employee_id)

        for child in children.get(employee_id, []):
            dfs(child)

        path.pop()
        del path_index[employee_id]

    for employee_id in children:
        if employee_id not in visited:
            dfs(employee_id)

    return cycles

def build_output(
    rows,
    validation_errors,
    accepted_rows,
    roots,
    managers,
    cycles
):
    accepted_employees = []

    for row in accepted_rows:
        accepted_employees.append({
            "employee_id": row["employee_id"],
            "employee_name": row["employee_name"],
            "email": row["email"]
        })

    root_employees = []

    for row in roots:
        root_employees.append({
            "employee_id": row["employee_id"],
            "employee_name": row["employee_name"]
        })

    return {
        "total_rows": len(rows),
        "invalid_rows": validation_errors,
        "accepted_employees": accepted_employees,
        "roots": root_employees,
        "managers": managers,
        "cycles": cycles
    }

def analyze_file(file_path):
    rows = parse_csv(file_path)
    rows = normalize_rows(rows)

    invalid_rows, accepted_rows, validation_errors = validate_employees(rows)

    roots, manager_of, manager_errors = manager_validation(accepted_rows)

    children = build_hierarchy(accepted_rows, manager_of)

    cycles = find_cycles(children)

    direct_reports = count_direct_reports(children)

    managers = get_managers(
        accepted_rows,
        direct_reports
    )

    output = build_output(
        rows,
        validation_errors,
        accepted_rows,
        roots,
        managers,
        cycles
    )

    return output


if __name__ == "__main__":
    file_path = sys.argv[1]

    output = analyze_file(file_path)

    print(json.dumps(output, indent=4))