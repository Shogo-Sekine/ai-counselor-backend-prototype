```bash
# curlで投げた時のレスポンスを正しく出すため
brew install jq

brew install pyenv

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

pyenv install 3.11.9
pyenv local 3.11.9
python --version
# Python 3.11.9

pip --version
# pip 24.0 from /Users/gangun/.pyenv/versions/3.11.9/lib/python3.11/site-packages/pip (python 3.11)

pip install -r requirements.txt

docker build -t ai-counselor-backend-prototype .
```