module.exports = {
  apps: [
    {
      name: "silas-frontend",
      cwd: "/home/silas/OpenJarvis/frontend",
      script: "npm",
      args: "start",
      interpreter: "none",
      env: {
        NODE_ENV: "production"
      },
      watch: false,
      max_memory_restart: "300M",
      error_file: "/home/silas/.pm2/logs/silas-frontend-error.log",
      out_file: "/home/silas/.pm2/logs/silas-frontend-out.log",
      merge_logs: true,
      autorestart: true,
      restart_delay: 2000
    }
  ]
}
