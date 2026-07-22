module.exports = {
  apps: [
    {
      name: "changeflow",
      script: "changeflow.py",
      interpreter: ".venv\\Scripts\\python.exe",
      cwd: "D:/Application/python/ChangeFlow_Application/backend",
      autorestart: true,
      watch: false
    }
  ]
};