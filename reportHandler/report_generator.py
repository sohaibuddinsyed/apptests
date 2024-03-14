"""
   This script will generate report for tests
   Author: Sohaib Uddin Syed (sohaibuddinsyed@ufl.edu), June 2023 - Present 
"""

import config
import time
import json
from loguru import logger
from datetime import datetime
from rich.console import Console
from rich.table import Table

JobStatus = config.JobStatus
TestStatus = config.TestStatus

class Color:
    UNAVAILABLE = "[blue]"
    INPROGRESS = "[cyan]"
    SUCCESS = "[green]"
    WARNING = "[yellow]"
    FAIL = "[red]"

def generate_failed_data(invalid_input_cnt, tests_missing_cnt):
    '''
        Generates and populates wrong/missing inputs test summary
    '''
    # Invalid jobs and tests summary
    failed_table = Table(title="Wrong/missing inputs")        
    failed_table.add_column("Invalid Modules", justify="center", style="red")
    failed_table.add_column("Missing Test files", justify="center", style="red")
    failed_table.add_row(str(invalid_input_cnt), str(tests_missing_cnt))
    return failed_table

def generate_summary_data(jobs_submitted_cnt, tests_passed_cnt, tests_failed_cnt):
    '''
        Generates and populates test result summary in the summary table
    '''
    # Summary of the main table
    summary_table = Table(title="Test Summary - Modules which were tested")
    summary_table.add_column("Total jobs submitted", justify="center")
    summary_table.add_column("Tests Passed", justify="center", style="green")
    summary_table.add_column("Tests Failed", justify="center", style="red")
    summary_table.add_row(str(jobs_submitted_cnt), str(tests_passed_cnt), str(tests_failed_cnt))
    return summary_table

def generate_report_data(table, report_name, args):
    '''
        Populates test result in the main table,
        Generates .txt and .json report files
    '''
    add_all_columns = True if "All" in args.output else False
    json_dict = {}

    # Variables to track various metrics
    tests_passed_cnt, tests_failed_cnt, jobs_submitted_cnt, invalid_input_cnt, tests_missing_cnt = 0, 0, 0, 0, 0

    # Process each test status and generate row data
    for i in range(len(config.RUNNING_TESTS)):
        curr_row = []
        curr_json_obj = {}
        curr_test = config.RUNNING_TESTS[i]
        
        # Process job status
        job_color = Color.FAIL
        if curr_test.jobStatus == JobStatus.SUBMITTED:
            job_color = Color.SUCCESS
            jobs_submitted_cnt += 1
        elif curr_test.jobStatus == JobStatus.PENDING:
            job_color = Color.INPROGRESS
        elif curr_test.jobStatus == JobStatus.INVALID:
            invalid_input_cnt += 1
        elif curr_test.jobStatus == JobStatus.MISSING:
            tests_missing_cnt += 1
            job_color = Color.WARNING
        elif curr_test.endTime is None:
            curr_test.endTime = time.time()

        # Process test status
        testColor = Color.FAIL
        if curr_test.testStatus == TestStatus.RUNNING:
            testColor = Color.INPROGRESS
        elif curr_test.testStatus == TestStatus.NA:
            testColor = Color.UNAVAILABLE
        elif curr_test.testStatus == TestStatus.COMPLETED:
            tests_passed_cnt += 1
            testColor = Color.SUCCESS
            if curr_test.endTime is None:
                curr_test.endTime = time.time()
        elif curr_test.testStatus == TestStatus.FAILED:
            tests_failed_cnt += 1
            if curr_test.endTime is None:
                curr_test.endTime = time.time()

        # Calculate duration
        if curr_test.endTime is not None:
            elapsedSeconds = curr_test.endTime - curr_test.startTime
        else:
            elapsedSeconds = time.time() - curr_test.startTime

        elapsedTime = time.strftime('%H:%M:%S', time.gmtime(elapsedSeconds))
        
        # Append all data as a row
        moduleName = curr_test.module
        curr_row.append(str(i + 1))

        if add_all_columns or "Module" in args.output:
            curr_row.append(moduleName)
            curr_json_obj["Module"] = moduleName

        if add_all_columns or "Dependency" in args.output:
            curr_row.append(curr_test.dependencies) 
            curr_json_obj["Dependency"] = curr_test.dependencies

        if add_all_columns or "TestFile" in args.output:
            curr_row.append(curr_test.filepath)
            curr_json_obj["TestFile"] = curr_test.filepath

        if add_all_columns or "Time" in args.output:
            curr_row.append(f"{elapsedTime}") 
            curr_json_obj["Time"] = elapsedTime

        if add_all_columns or "JobId" in args.output:
            curr_row.append(curr_test.jobId)
            curr_json_obj["JobId"] = curr_test.jobId

        if add_all_columns or "JobStatus" in args.output:
            curr_row.append(job_color + f"{curr_test.jobStatus.value}")
            curr_json_obj["JobStatus"] = curr_test.jobStatus.value

        if add_all_columns or "TestStatus" in args.output:
            curr_row.append(testColor + f"{curr_test.testStatus.value}")
            curr_json_obj["TestStatus"] = curr_test.testStatus.value

        if add_all_columns or "ExitCode" in args.output:
            curr_row.append(testColor + f"{curr_test.exitCode}")
            curr_json_obj["ExitCode"] = curr_test.exitCode

        # Add row into the table and json file
        table.add_row(*curr_row)
        json_dict["sno_" + str(i + 1)] = curr_json_obj

    # Generate summary after the report is complete
    summaryTable = generate_summary_data(jobs_submitted_cnt, tests_passed_cnt, tests_failed_cnt)
    failedTable = generate_failed_data(invalid_input_cnt, tests_missing_cnt)
    
    with open(report_name + ".json", "wt") as json_file:
        json_file.write(json.dumps(json_dict, indent=4))

    return table, summaryTable, failedTable

def generate_report_schema(args):
    '''
        Generate schema for the report table
    '''

    add_all_columns = True if "All" in args.output else False
    table = Table(min_width=200)

    table.add_column("Sno", justify="left", style="cyan", no_wrap=True)

    if add_all_columns or "Module" in args.output:
        table.add_column("Module/Version", style="magenta", no_wrap=True)

    if add_all_columns or "Dependency" in args.output:
        table.add_column("Dependencies", style="green",no_wrap=True)

    if add_all_columns or "TestFile" in args.output:
        table.add_column("Test File", style="cyan")

    if add_all_columns or "Time" in args.output:
        table.add_column("Duration", style="magenta", no_wrap=True)

    if add_all_columns or "JobId" in args.output:
        table.add_column("Job Id", style="green", no_wrap=True)

    if add_all_columns or "JobStatus" in args.output:
        table.add_column("Job Status", style="cyan", no_wrap=True)

    if add_all_columns or "TestStatus" in args.output:
        table.add_column("Test Status", no_wrap=True)

    if add_all_columns or "ExitCode" in args.output:
        table.add_column("Exit Code", style="green", no_wrap=True)
    
    return table

def generate_report(testStartTime, args, exit=False):
    '''
        Driver method to generate report (.txt, .json) with all the required tables
    '''
    report_name = config.REPORT_PATH + testStartTime
    with open(report_name + ".txt", "wt") as report_file:
        console = Console(file=report_file, width=750)

        # Report headers
        if not exit:
            console.print("Test Status: Testing is in progress...... (Reload file for new results)\n")
        else:
            console.print("Test Status: Testing Complete!\n")
        console.print(f"Test Report : {datetime.now()}")

        # Generate main table schema
        table = generate_report_schema(args)

        # Populate main table along with summary and failed status tables
        table, summaryTable, failedTable = generate_report_data(table, report_name, args)

        # Write all tables to .txt file
        console.print(table)
        console.print(summaryTable)
        console.print(failedTable)

        logger.debug("Latest report generated in " + report_name)