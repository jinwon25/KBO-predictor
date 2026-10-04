"""공개할 추적 파일과 새 파일의 형식·인증 정보·운영 주소를 검사합니다."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'.py', '.md', '.html', '.css', '.js', '.yml', '.png'}
SKIP = {'.git', '__pycache__', '.venv', 'venv', 'reports'}


def files():
    if (ROOT / '.git').is_dir():
        output = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT)
        return [ROOT / name.decode('utf-8') for name in output.split(b'\0') if name and (ROOT / name.decode('utf-8')).is_file()]
    return [p for p in ROOT.rglob('*') if p.is_file() and not SKIP.intersection(p.relative_to(ROOT).parts)]


def inspect(paths):
    errors = []
    patterns = [r'-----BEGIN ' + r'(?:RSA |OPENSSH |EC )?PRIVATE KEY',
                r'gh' + r'[opusr]_[A-Za-z0-9]{30,}',
                r'AK' + r'IA[0-9A-Z]{16}',
                r'(?i)(?:api_key|password|access_token)\s*[:=]\s*[\x22\x27][^\x22\x27\s]{8,}']
    for path in paths:
        name = path.relative_to(ROOT).as_posix()
        if path.is_symlink():
            errors.append(f'{name}: symlinks are not allowed')
            continue
        if path.name not in ('.gitignore', '.gitattributes', 'LICENSE') and path.suffix not in ALLOWED:
            errors.append(f'{name}: non-allowlisted file type')
        if path.stat().st_size > 2_000_000:
            errors.append(f'{name}: unusually large file')
        if path.suffix == '.png':
            if not name.startswith('docs/images/demo-'):
                errors.append(f'{name}: only reviewed synthetic screenshots allowed')
            continue
        text = path.read_text(encoding='utf-8')
        if any(re.search(pattern, text) for pattern in patterns):
            errors.append(f'{name}: potential credential pattern')
        for address in re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text):
            if address != '127.0.0.1':
                errors.append(f'{name}: non-loopback address')
        if re.search(r'[A-Z]:\\', text):
            errors.append(f'{name}: local absolute Windows path')
    return errors


if __name__ == '__main__':
    selected = files()
    issues = inspect(selected)
    for issue in issues:
        print(issue)
    print(f'공개 파일 {len(selected)}개 검사, 발견 사항 {len(issues)}건.')
    raise SystemExit(bool(issues))
