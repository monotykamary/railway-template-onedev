# Deploy and Host OneDev with Railway

OneDev is a self-hosted development platform combining Git repositories, pull requests, issue tracking, Kanban boards, package registries, and CI/CD orchestration. This core Railway template deploys the OneDev server with managed PostgreSQL and durable application storage while intentionally leaving job execution to separately attached agents.

## About Hosting OneDev

Hosting OneDev requires preserving both its relational database and its application-data directory. The database stores platform metadata, while `/opt/onedev` contains repositories, attachments, artifacts, and server state. This template connects OneDev to a private Railway PostgreSQL service, mounts persistent storage at the official data path, initializes the administrator account, and exposes the web interface over Railway HTTPS.

The template does not configure a local CI executor. Railway does not provide the Docker socket or privileged nested-container support required by OneDev's Docker executors. Builds remain unassigned until a compatible external agent or shell executor is configured.

## Common Use Cases

- Host private Git repositories and review pull requests
- Manage issues, iterations, and Kanban boards
- Publish and consume project packages
- Centralize source code and project activity for a small team
- Use OneDev as a control plane for external build agents

## Dependencies for OneDev Hosting

- OneDev 16.3.0
- PostgreSQL
- Persistent storage mounted at `/opt/onedev`
- Railway HTTPS networking on port `6610`

### Deployment Dependencies

- [OneDev documentation](https://docs.onedev.io/)
- [OneDev source and issue tracker](https://code.onedev.io/onedev/server)
- [OneDev agent documentation](https://docs.onedev.io/administration-guide/agent-management)
- [Template source repository](https://github.com/monotykamary/railway-template-onedev)

### Implementation Details

OneDev publishes its fixed HTTP port `6610` through Railway's `PORT` routing variable and uses its supported PostgreSQL dialect and JDBC configuration over Railway's private network. The official application image is pinned rather than following a mutable tag. First-run initialization creates the administrator and canonical HTTPS server URL. No Docker socket is mounted and no job executor is configured. The Railway health check targets the web root after database migration and application startup.

### Why Deploy OneDev on Railway?

Railway provides managed PostgreSQL, private service networking, durable volumes, HTTPS domains, health checks, deployment logs, and restart management. This removes host and certificate administration while retaining OneDev's integrated code-management experience. External agents can later connect outbound to the public OneDev URL when CI capacity is required.
