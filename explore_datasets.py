import pandas as pd

# ---- Dataset 1: GitHub Issues ----
df_issues = pd.read_csv(r"C:/Users/lap.lk/Desktop/Research 4.1/github_issues.csv")  # adjust filename

print("=== GITHUB ISSUES DATASET ===")
print("Shape:", df_issues.shape)
print("Columns:", df_issues.columns.tolist())
print("\nFirst 3 rows:")
print(df_issues.head(3))
print("\nMissing values:")
print(df_issues.isnull().sum())

# ---- Dataset 2: Sprint Velocity ----
df_sprint = pd.read_csv(r"C:/Users/lap.lk/Desktop/Research 4.1/Aurora Sprints 41.csv")
df_sprint = pd.read_csv(r"C:/Users/lap.lk/Desktop/Research 4.1/MESO Sprints 96.csv")
df_sprint = pd.read_csv(r"C:/Users/lap.lk/Desktop/Research 4.1/Spring XD Sprints 67.csv.csv")
df_sprint = pd.read_csv(r"C:/Users/lap.lk/Desktop/Research 4.1/Usergrid Sprints 36.csv")  # adjust filename

print("\n=== SPRINT VELOCITY DATASET ===")
print("Shape:", df_sprint.shape)
print("Columns:", df_sprint.columns.tolist())
print("\nFirst 3 rows:")
print(df_sprint.head(3))
print("\nMissing values:")
print(df_sprint.isnull().sum())


import pandas as pd
import os

# Build the path safely
folder = os.path.join("C:\\", "Users", "lap.lk", "Desktop", "Research 4.1")
file = os.path.join(folder, "github_issues.csv")

print("Looking for file at:", file)
print("File exists:", os.path.exists(file))

df_issues = pd.read_csv(file)
print("Shape:", df_issues.shape)
print("Columns:", df_issues.columns.tolist())
print(df_issues.head(3))

import os

# Check step by step
print("Step 1 - Does the folder exist?")
print(os.path.exists("C:/Users/lap.lk/Desktop/Research 4.1/Datasets RAW"))

print("\nStep 2 - All files in the folder:")
for f in os.listdir("C:/Users/lap.lk/Desktop/Research 4.1/Datasets RAW"):
    print(" -", repr(f))



import pandas as pd
import os

# ============================================
# DATASET 1 - GitHub Issues (Priority Prediction)
# ============================================
path1 = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1", "github_issues.csv")

print("=" * 50)
print("DATASET 1 - GITHUB ISSUES")
print("=" * 50)
print("Looking at:", path1)
print("File found:", os.path.exists(path1))

df_issues = pd.read_csv(path1)

print("Shape (rows, columns):", df_issues.shape)
print("\nColumn names:")
for col in df_issues.columns:
    print(" -", col)
print("\nFirst 3 rows:")
print(df_issues.head(3))
print("\nMissing values per column:")
print(df_issues.isnull().sum())

# ============================================
# DATASET 2 - Aurora Sprints (Effort Estimation)
# ============================================
path2 = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1", "Aurora Sprints 41.csv")

print("\n" + "=" * 50)
print("DATASET 2 - AURORA SPRINTS")
print("=" * 50)
print("Looking at:", path2)
print("File found:", os.path.exists(path2))

df_aurora = pd.read_csv(path2)

print("Shape (rows, columns):", df_aurora.shape)
print("\nColumn names:")
for col in df_aurora.columns:
    print(" -", col)
print("\nFirst 3 rows:")
print(df_aurora.head(3))
print("\nMissing values per column:")
print(df_aurora.isnull().sum())

# ============================================
# DATASET 3 - MESO Sprints
# ============================================
path3 = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1", "MESO Sprint 96.csv")

print("\n" + "=" * 50)
print("DATASET 3 - MESO SPRINTS")
print("=" * 50)
print("Looking at:", path3)
print("File found:", os.path.exists(path3))

df_meso = pd.read_csv(path3)

print("Shape (rows, columns):", df_meso.shape)
print("\nColumn names:")
for col in df_meso.columns:
    print(" -", col)
print("\nFirst 3 rows:")
print(df_meso.head(3))
print("\nMissing values per column:")
print(df_meso.isnull().sum())

# ============================================
# DATASET 4 - Spring XD Sprints
# ============================================
path4 = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1", "Spring XD Sprints 67.csv")

print("\n" + "=" * 50)
print("DATASET 4 - SPRING XD SPRINTS")
print("=" * 50)
print("Looking at:", path4)
print("File found:", os.path.exists(path4))

df_springxd = pd.read_csv(path4)

print("Shape (rows, columns):", df_springxd.shape)
print("\nColumn names:")
for col in df_springxd.columns:
    print(" -", col)
print("\nFirst 3 rows:")
print(df_springxd.head(3))
print("\nMissing values per column:")
print(df_springxd.isnull().sum())

# ============================================
# DATASET 5 - Usergrid Sprints
# ============================================
path5 = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1", "Usergrid Sprints 36.csv")

print("\n" + "=" * 50)
print("DATASET 5 - USERGRID SPRINTS")
print("=" * 50)
print("Looking at:", path5)
print("File found:", os.path.exists(path5))

df_usergrid = pd.read_csv(path5)

print("Shape (rows, columns):", df_usergrid.shape)
print("\nColumn names:")
for col in df_usergrid.columns:
    print(" -", col)
print("\nFirst 3 rows:")
print(df_usergrid.head(3))
print("\nMissing values per column:")
print(df_usergrid.isnull().sum())

print("\n" + "=" * 50)
print("ALL DATASETS LOADED SUCCESSFULLY!")
print("=" * 50)


import pandas as pd
import os

base = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1","Datasets RAW")

# First let's see what files were extracted
print("Files in your Research 4.1 folder:")
for f in os.listdir(base):
    print(" -", f)



import pandas as pd
import os

base = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1","Datasets RAW")

# Load the priority dataset
path = os.path.join(base, "cross-project_norm.csv")

df_priority = pd.read_csv(path)

print("Shape:", df_priority.shape)
print("\nColumn names:")
for col in df_priority.columns:
    print(" -", col)
print("\nFirst 3 rows:")
print(df_priority.head(3))
print("\nMissing values:")
print(df_priority.isnull().sum())
print("\nPriority distribution:")
print(df_priority.iloc[:, -1].value_counts())



import pandas as pd
import os

base = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1", "Datasets RAW")
path = os.path.join(base, "cross-project_norm.csv")
df_priority = pd.read_csv(path)

# Check the actual target columns
print("=== actual_label_cat distribution ===")
print(df_priority["actual_label_cat"].value_counts())

print("\n=== repo_label_biclass distribution ===")
print(df_priority["repo_label_biclass"].value_counts())

print("\n=== ft_issue_type distribution ===")
print(df_priority["ft_issue_type"].value_counts())