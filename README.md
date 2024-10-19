# Home finance analysis

**Goal**:
Create application which allows to plot graphs based on the incomes/expenses
of the household with some forecasting for future incomes/expenses
to provide user common understand of his finance state.

## How to use

Right now all manipulations only available inside the code.  

- Just write down your incomes/expenses in excel sheets.
  Use `./data/template.xlsx` as your boilerplate.
  The more you have data, the better for forecasting.
- Load your data.  
- Choose time period as baseline for forecast.  
- Choose time period for graphs.  
- Use forecast methods.  
- Create graphs.  

## template.xlsx structure

Sheet names consists of `{Month}_{year}` for example: **January_2024**

![template_structure](template_structure.png)

1. Data header. **SHOULD NOT** be changed *(used in the code as reference point)*.  
2. Savings header. **SHOULD NOT** be changed *(used in the code as reference point)*.  
3. Incomes header. Could be changed *(names and count of the columns)*.
4. Expenses header. Could be changed *(names and count of the columns)*.  
   Headers for columns **always** should have **2-levels**.
