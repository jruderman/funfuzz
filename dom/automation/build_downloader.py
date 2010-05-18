#!/usr/bin/env python

import re, os, shutil, subprocess, time, StringIO
devnull = open(os.devnull, "w")

# Use curl rather than urllib because curl can check certificates.
def readFromURL(url):
  p = subprocess.Popen(["curl", "--silent", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  (out, err) = p.communicate()
  return StringIO.StringIO(out)
def downloadURL(url, dest):
  subprocess.check_call(["curl", "--output", dest, url])
  return dest

def httpDirList(dir):
  print "Looking in " + dir + "..."
  files = []
  page = readFromURL(dir)
  for line in page:
    if line.startswith("<tr>"):
      match = re.search("<a href=\"([^\"]*)\">", line)
      if match != None and match.group(1)[0] != "/":
        files.append(dir + match.group(1))
  page.close()
  return files


def unzip(fn, dest):
  subprocess.check_call(["unzip", fn, "-d", dest], stdout=devnull)

def untarbz2(fn, dest):
  os.mkdir(dest)
  subprocess.check_call(["tar", "-C", dest, "-xjf", os.path.abspath(fn)], stdout=devnull)

def undmg(fn, dest, mountpoint):
  subprocess.check_call(["hdiutil", "attach", "-quiet", "-mountpoint", mountpoint, fn], stdout=devnull)
  try:
    #while not os.path.exists(mountpoint + "/MinefieldDebug.app"):
    #  print "waiting for disk image"
    #  time.sleep(1)
    shutil.copytree(mountpoint + "/MinefieldDebug.app", dest + "/MinefieldDebug.app")
  finally:
    subprocess.check_call(["hdiutil", "detach", mountpoint], stdout=devnull)


def downloadBuild(httpDir, wantSymbols=False, wantTests=True):
  if os.path.exists("build"):
    shutil.rmtree("build")
  os.mkdir("build")
  downloadDir = os.path.join("build", "download")
  os.mkdir(downloadDir)
  appDir = os.path.join("build", "dist") + os.sep # calling this "dist" makes os.path.join(reftestScriptDir, automation.DEFAULT_APP) work
  testsDir = os.path.join("build", "tests") + os.sep
  symbolsDir = os.path.join("build", "symbols") + os.sep
  for remotefn in httpDirList(httpDir):
    localfn = os.path.join(downloadDir, remotefn.split("/")[-1])
    if remotefn.endswith(".linux-i686.tar.bz2"):
      print "Downloading application..."
      untarbz2(downloadURL(remotefn, localfn), appDir)
    if remotefn.endswith(".win32.zip"):
      print "Downloading application..."
      unzip(downloadURL(remotefn, localfn), appDir)
    if remotefn.endswith(".mac.dmg"):
      print "Downloading application..."
      undmg(downloadURL(remotefn, localfn), appDir, os.path.join("build", "MOUNTEDDMG"))
    if remotefn.endswith(".tests.zip") and wantTests:
      print "Downloading tests..."
      unzip(downloadURL(remotefn, localfn), testsDir)
    if remotefn.endswith(".crashreporter-symbols.zip") and wantSymbols:
      print "Downloading crash reporter symbols..."
      unzip(downloadURL(remotefn, localfn), symbolsDir)

def findLatestBuild(branchName, osName):
  buildsDir = "https://ftp.mozilla.org/pub/mozilla.org/firefox/tinderbox-builds/" + branchName + "-" + osName + "-debug/"
  latestBuild = httpDirList(buildsDir)[-1]
  return latestBuild

if __name__ == "__main__":
  latestBuild = findLatestBuild("mozilla-central", "macosx")
  downloadBuild(latestBuild)
