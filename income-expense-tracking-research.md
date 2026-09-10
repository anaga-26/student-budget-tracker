# Income and Expense Tracking Requirements Research

## 1. Introduction

The Student Budget Tracker is designed to help university and foundation students manage their personal finances. The Income and Expense Tracking module allows users to record and manage their financial transactions in a simple way.

## 2. Income Tracking Requirements

The system should allow users to record income received by the student.

Examples of income include:
- Monthly allowance from parents
- Part-time job income
- Other sources of student income

The system should store the relevant information for each income transaction so that users can keep track of their available money.

## Income Sources

The Student Budget Tracker should allow students to record different sources of income.

The identified income sources are:

- Monthly allowance from parents
- Part-time job income
- Other sources of student income

Each income source should be recorded as part of an income transaction so that students can keep track of the money they receive.

## Income Amount

The system should allow students to enter the amount of money received for each income transaction.

The income amount should be recorded as a numerical value so that students can keep track of the total money they receive.

## Income Date

The system should allow students to record the date when the income is received.

The income date should be stored with each income transaction so that students can keep track of when the money was received.

## Income Description

The system should allow students to enter a short description for each income transaction.

The description should help students identify the purpose or details of the income received.

## Document Income Requirements

The identified income recording requirements should be documented clearly so that they can be used when developing the Student Budget Tracker.


## 3. Expense Tracking Requirements

The system should allow users to record money spent by the student.

Examples of expenses include:
- Food
- Transportation
- Shopping
- Entertainment
- Daily necessities

Users should be able to record each expense as a separate transaction.

### Expense Amount

The system should allow students to enter the amount of money spent for each expense transaction.

The expense amount should be recorded as a numerical value so that students can keep track of their total spending.

### Expense Date

The system should allow students to record the date on which each expense occurred.

Recording the expense date helps students track their spending over time and understand when their money is being spent.

### Expense Types

The system should allow students to record different types of expenses.

Examples of expense types include:

- Food
- Transportation
- Accommodation
- Education
- Entertainment
- Other expenses

### Expense Description

The system should allow students to add a short description for each expense transaction.

The description can provide additional details about the expense, such as what the money was spent on.

### Document Expense Recording Requirements

The identified expense recording requirements should be documented clearly for use during the development of the Student Budget Tracker.

Each expense transaction should include important information such as the expense amount, expense date, expense type, and a short description.


## 4. Expense Categorisation Requirements

Expense transactions should be organised into categories to help users understand where their money is being spent.

The project specification identifies categories such as:
- Food and Dining
- Transportation
- Education
- Accommodation
- Bills and Utilities
- Healthcare
- Personal Care
- Entertainment
- Other

### Food Category

The Food Category includes expenses related to meals, drinks, groceries, snacks, and other food purchases.This category helps students monitor how much money they spend on their daily food needs.

### Transportation Category

The Transportation Category includes expenses related to public transport, fuel, e-hailing services, parking, and other travel costs. This category helps students monitor the amount of money spent on travelling to university and other places.

### Shopping Category

The Shopping Category includes expenses related to clothing, personal items, accessories, and other purchases.This category helps students monitor their spending on non-essential and personal shopping needs.

### Entertainment Category

The Entertainment Category includes expenses related to movies, games, streaming services, events, and other recreational activities. This category helps students monitor how much money they spend on entertainment and leisure activities.

### Daily Necessities Category

The Daily Necessities Category includes expenses for essential everyday items such as toiletries, hygiene products, household items, and other basic personal needs.This category helps students monitor their spending on important daily necessities.


## 5. Transaction Management Requirements

Users should be able to manage their recorded financial transactions.

The system should support:
- Adding income records
- Adding expense records
- Editing existing transactions
- Deleting existing transactions
- Viewing transaction history

### Editable Transaction Information

The Student Budget Tracker should allow users to edit the details of an existing transaction when incorrect information has been recorded.

The editable transaction information should include:

- Transaction amount
- Transaction date
- Transaction type
- Expense category
- Transaction description

Allowing these details to be edited helps students correct mistakes and keep their income and expense records accurate.

### Transaction Editing Process

The Student Budget Tracker should provide a simple process for users to edit an existing transaction.

The editing process should allow users to:

1. Select the transaction they want to edit.
2. View the existing transaction details.
3. Modify the required information.
4. Save the updated transaction.
5. Ensure that the updated information replaces the previous information.

The system should keep the transaction record updated so that users can maintain accurate income and expense records.

### Transaction Deletion Process

The Student Budget Tracker should allow users to remove an existing transaction when it is no longer required or was recorded by mistake.

The deletion process should allow users to:

1. Select the transaction they want to delete.
2. View the transaction details before deleting it.
3. Confirm that they want to delete the selected transaction.
4. Remove the transaction from the transaction records.
5. Update the transaction history after the deletion.

The deletion process should help users keep their transaction records organised and accurate.

### Delete Confirmation

The Student Budget Tracker should ask users to confirm before deleting a transaction.

The confirmation should clearly indicate that the selected transaction will be removed from the records.

The system should provide options to:

- Confirm the deletion and remove the transaction.
- Cancel the deletion and keep the transaction.

This confirmation step helps prevent users from accidentally deleting an important transaction.

### Error Handling

The Student Budget Tracker should provide appropriate feedback when an error occurs while editing or deleting a transaction.

The system should handle situations such as:

- The selected transaction cannot be found.
- The user enters invalid transaction information.
- The transaction cannot be updated successfully.
- The transaction cannot be deleted successfully.

The system should display a clear message to inform the user about the problem and allow them to try again.

## 6. Transaction Information Requirements

Each transaction should contain important information needed for financial tracking.

The project specification identifies:
- Transaction amount
- Transaction category
- Transaction type
- Transaction date

The transaction type should identify whether the record is an income or an expense.

## 7. Data Storage Requirements

The system will use an SQLite database to store financial transaction records. The database should allow the system to insert, update, and retrieve transaction information when users manage their income and expenses.

## 8. Research Findings

Based on the project requirements, the Income and Expense Tracking module needs to provide a simple way for students to record, organise, view, edit, and delete their financial transactions.

The main requirements identified are income recording, expense recording, expense categorisation, transaction information, transaction history, and transaction editing and deletion.

## 9. Conclusion

The research shows that the Income and Expense Tracking module is an important part of the Student Budget Tracker. It should provide students with a simple and organised way to monitor their income and spending activities.