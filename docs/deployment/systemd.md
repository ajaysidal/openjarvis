# systemd Service (Linux)

Silas includes a systemd unit file for running the API server as a managed background service on Linux. This provides automatic startup on boot, crash recovery, and integration with standard Linux service management tools.

## Prerequisites

Before installing the service, ensure that:

1. Silas is installed in a virtual environment at `/opt/silas/.venv` (or adjust paths accordingly).
2. A dedicated `silas` system user exists (recommended for security).
3. An inference engine (such as Ollama) is running and accessible.

Create the user and installation directory:

```bash
sudo useradd --system --create-home --home-dir /opt/silas silas
sudo -u silas python3 -m venv /opt/silas/.venv
sudo -u silas git clone https://github.com/open-jarvis/Silas.git /opt/silas/Silas
cd /opt/silas/Silas && sudo -u silas uv sync --extra server
```

## Installing the Service

The unit binds `0.0.0.0`, so an **API key is required** — and the unit
declares `EnvironmentFile=/etc/silas/env` (no `-` prefix), so it will
**fail to start** until that file exists with a key. Create it first:

```bash
sudo mkdir -p /etc/silas
echo "SILAS_API_KEY=$(jarvis auth generate-key)" | sudo tee /etc/silas/env
sudo chmod 600 /etc/silas/env
```

Then copy the unit file, reload the daemon, and enable the service:

```bash
sudo cp deploy/systemd/silas.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable silas
sudo systemctl start silas
```

Clients must send `Authorization: Bearer <key>` on `/v1/*` and `/api/*`
requests. (If you instead bind to `127.0.0.1`, the key is optional and you
can drop the `EnvironmentFile` line.)

Verify it is running:

```bash
sudo systemctl status silas
```

## Service File Reference

The provided unit file at `deploy/systemd/silas.service`:

```ini
[Unit]
Description=Silas API Server
After=network.target

[Service]
Type=simple
User=silas
WorkingDirectory=/opt/silas
ExecStart=/opt/silas/.venv/bin/jarvis serve --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5
Environment=HOME=/opt/silas

[Install]
WantedBy=multi-user.target
```

### `[Unit]` Section

| Directive     | Value              | Description                                                                 |
|---------------|--------------------|-----------------------------------------------------------------------------|
| `Description` | `Silas API Server` | Human-readable name shown in `systemctl status` and logs.              |
| `After`       | `network.target`   | Delays startup until the network stack is available, since the server binds to a network socket and may need to reach a remote engine. |

### `[Service]` Section

| Directive          | Value                                                              | Description                                                                                     |
|--------------------|--------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `Type`             | `simple`                                                           | The process started by `ExecStart` is the main service process. systemd considers the service started immediately. |
| `User`             | `silas`                                                       | Runs the server as the `silas` user rather than root, limiting the blast radius of any security issue. |
| `WorkingDirectory` | `/opt/silas`                                                  | Sets the working directory for the process. This is where Silas looks for local files and writes data. |
| `ExecStart`        | `/opt/silas/.venv/bin/jarvis serve --host 0.0.0.0 --port 8000` | The command to start the server. Uses the full path to the `jarvis` binary inside the virtual environment. |
| `Restart`          | `on-failure`                                                       | Automatically restarts the service if it exits with a non-zero exit code. Does not restart on clean shutdown (`systemctl stop`). |
| `RestartSec`       | `5`                                                                | Waits 5 seconds before attempting a restart, preventing rapid restart loops if the service crashes immediately on startup. |
| `Environment`      | `HOME=/opt/silas`                                             | Sets the `HOME` environment variable so Silas finds its configuration at `~/.silas/config.toml` (resolving to `/opt/silas/.silas/config.toml`). |

### `[Install]` Section

| Directive    | Value               | Description                                                                                 |
|--------------|---------------------|---------------------------------------------------------------------------------------------|
| `WantedBy`   | `multi-user.target` | The service starts when the system reaches multi-user mode (standard boot target for servers). `systemctl enable` creates a symlink under this target. |

## Configuration Options

### Changing the Bind Address and Port

Edit the `ExecStart` line to change the host or port:

```ini
ExecStart=/opt/silas/.venv/bin/jarvis serve --host 127.0.0.1 --port 9000
```

!!! tip
    Binding to `127.0.0.1` restricts access to localhost only. Use this when running behind a reverse proxy like Nginx or Caddy.

### Setting the Engine and Model

Pass additional flags to `jarvis serve`:

```ini
ExecStart=/opt/silas/.venv/bin/jarvis serve --host 0.0.0.0 --port 8000 --engine ollama --model qwen3:8b
```

### Adding Environment Variables

Add multiple `Environment` directives or use `EnvironmentFile` for complex configurations:

```ini
[Service]
Environment=HOME=/opt/silas
Environment=SILAS_ENGINE_DEFAULT=vllm
Environment=SILAS_OLLAMA_HOST=http://localhost:11434
```

Or load from a file:

```ini
[Service]
EnvironmentFile=/opt/silas/.env
```

### Changing the User

If you prefer a different service user, update both the `User` directive and the paths:

```ini
[Service]
User=myuser
WorkingDirectory=/home/myuser/silas
ExecStart=/home/myuser/silas/.venv/bin/jarvis serve --host 0.0.0.0 --port 8000
Environment=HOME=/home/myuser/silas
```

### Using a Configuration File

Ensure the configuration file exists at the path where `HOME` points:

```bash
sudo -u silas mkdir -p /opt/silas/.silas
sudo -u silas cp config.toml /opt/silas/.silas/config.toml
```

The server reads `~/.silas/config.toml` on startup, where `~` resolves from the `HOME` environment variable.

## Viewing Logs

Silas logs are captured by journald. View them with `journalctl`:

```bash
# View all logs for the service
sudo journalctl -u silas

# Follow logs in real time
sudo journalctl -u silas -f

# View logs since the last boot
sudo journalctl -u silas -b

# View logs from the last hour
sudo journalctl -u silas --since "1 hour ago"

# View only error-level messages
sudo journalctl -u silas -p err
```

## Managing the Service

### Start, Stop, and Restart

```bash
# Start the service
sudo systemctl start silas

# Stop the service
sudo systemctl stop silas

# Restart the service (stop + start)
sudo systemctl restart silas

# Reload configuration without full restart (sends SIGHUP)
sudo systemctl reload-or-restart silas
```

### Check Status

```bash
sudo systemctl status silas
```

Example output:

```
● silas.service - Silas API Server
     Loaded: loaded (/etc/systemd/system/silas.service; enabled; preset: enabled)
     Active: active (running) since Fri 2026-02-21 10:00:00 UTC; 2h ago
   Main PID: 12345 (jarvis)
      Tasks: 4 (limit: 4915)
     Memory: 256.0M
        CPU: 1min 23s
     CGroup: /system.slice/silas.service
             └─12345 /opt/silas/.venv/bin/python /opt/silas/.venv/bin/jarvis serve --host 0.0.0.0 --port 8000
```

### Enable and Disable on Boot

```bash
# Enable automatic start on boot
sudo systemctl enable silas

# Disable automatic start on boot
sudo systemctl disable silas
```

### Apply Changes After Editing the Unit File

After modifying `/etc/systemd/system/silas.service`, reload the systemd daemon and restart the service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart silas
```

## Running Alongside Ollama

If Ollama is also managed via systemd, you can add an ordering dependency so the Silas service waits for Ollama to start:

```ini
[Unit]
Description=Silas API Server
After=network.target ollama.service
Requires=ollama.service
```

| Directive  | Description                                                              |
|------------|--------------------------------------------------------------------------|
| `After`    | Ensures Silas starts after Ollama.                                  |
| `Requires` | If Ollama fails to start, Silas will not start either.              |

!!! note
    Use `Wants` instead of `Requires` if you want Silas to start even when Ollama is unavailable (for example, if you plan to start Ollama manually later).
