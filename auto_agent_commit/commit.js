const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

const logFile = path.join(__dirname, 'plugin.log');
const log = (msg) => fs.appendFileSync(logFile, msg + '\n');

try {
    const rawInput = fs.readFileSync(0, 'utf-8');
    const payload = rawInput.trim() ? JSON.parse(rawInput) : {};

    const targetDir = payload.workspacePaths?.[0] || process.cwd();
    process.chdir(targetDir);
    log(`Working directory: ${targetDir}`);

    execSync('git add .', { stdio: 'pipe' });

    const statusOutput = execSync('git status --porcelain', { stdio: 'pipe' }).toString().trim();
    if (!statusOutput) {
        log('No changes detected.');
        console.log(JSON.stringify({ status: "skipped", reason: "no_changes" }));
        process.exit(0);
    }

    const modelName = payload.activeModel || "Antigravity Agent";
    const commitMsg = `chore(agent): auto-commit via ${modelName}\n\nModified files:\n${statusOutput}`;

    execSync(`git commit -m "${commitMsg}"`, { stdio: 'pipe' });
    log('Commit successful.');

    console.log(JSON.stringify({ status: "success", commit_message: commitMsg }));

} catch (err) {
    log(`Error: ${err.message}\n${err.stack}`);
    console.log(JSON.stringify({ status: "failed", error: err.message }));
}