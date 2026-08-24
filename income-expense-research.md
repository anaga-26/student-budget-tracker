# Income and Expense Tracking Requirements

## Purpose

The Student Budget Tracker should allow students to record and manage their income and expenses so they can monitor their financial activities.

## Income Tracking

The system should allow users to record income transactions.

Income records should include:
- Amount
- Category
- Date
- Transaction type

The transaction type should identify the record as income.

## Expense Tracking

The system should allow users to record expense transactions.

Expense records should include:
- Amount
- Category
- Date
- Transaction type

The transaction type should identify the record as an expense.

## Transaction Storage

Income and expense transactions should be stored in the SQLite database.

The transaction table should contain:
- transaction_id
- user_id
- amount
- category
- type
- date

## Budget Monitoring

The system should use recorded transactions to calculate the user's remaining balance.

If spending exceeds the user's monthly budget, the system should display a warning message.

## Reports and Analysis

The system should provide reports and charts to help users understand their spending patterns.

## Technology

The system will use Python and Tkinter for the application interface and SQLite for storing financial transaction records.