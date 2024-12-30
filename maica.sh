# Check the current branch name
git branch

# If the current branch is master, push to origin master
git push origin master

# (Optional) Rename the local branch from master to main
git branch -m master main
git push origin main
git branch -u origin/main main