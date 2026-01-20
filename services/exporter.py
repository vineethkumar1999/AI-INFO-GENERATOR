import json
from openpyxl import Workbook

def export_to_excel(testcases_json, file_path="test_cases.xlsx"):
    data = json.loads(testcases_json)
    test_cases = data["test_cases"]

    wb = Workbook()
    ws = wb.active
    ws.title = "Test Cases"

    headers = [
        "Test Case ID",
        "Title",
        "Preconditions",
        "Steps",
        "Expected Result",
        "Type"
    ]

    ws.append(headers)

    for tc in test_cases:
        ws.append([
            tc["id"],
            tc["title"],
            tc["preconditions"],
            "\n".join(tc["steps"]),
            tc["expected_result"],
            tc["type"]
        ])

    wb.save(file_path)
    return file_path
