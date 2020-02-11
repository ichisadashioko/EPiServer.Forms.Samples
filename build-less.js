const fs = require("fs");
const path = require("path");
const less = require("less");

const IGNORE_FILES = [
    ".git",
    "bin",
    "obj",
    "node_modules",
];

/**
 * Check the file name should be iterated or not. Ignored files are listed in `IGNORE_FILES`.
 * @param {string} inPath 
 */
function isIgnore(inPath) {
    for (let i = 0; i < IGNORE_FILES.length; i++) {
        if (inPath === IGNORE_FILES[i]) {
            return true;
        }
    }

    return false;
}

/**
 * Find all `.less` files given the input path.
 * @param {string} inPath 
 * @returns {string[]} List of file paths.
 */
function findLessFiles(inPath) {
    // console.log(inPath);
    let lessFiles = [];

    let basename = path.basename(inPath);

    if (isIgnore(basename)) {
        return lessFiles;
    }

    let fileStat = fs.lstatSync(inPath);

    if (fileStat.isSymbolicLink()) {
        return lessFiles;
    }

    if (fileStat.isFile()) {
        let ext = path.extname(inPath).toLocaleLowerCase();
        if (ext === '.less') {
            lessFiles.push(inPath);
        }
    } else {
        let childFiles = fs.readdirSync(inPath)

        childFiles.forEach(child => {
            let childPath = path.join(inPath, child)
            lessFiles = lessFiles.concat(findLessFiles(childPath));
        });
    }

    return lessFiles;
}

/**
 * Compile less file to css file.
 * @param {string} inPath 
 * @param {string} outPath 
 */
function compileLessFile(inPath, outPath) {
    let lessStr = fs.readFileSync(inPath, "utf8");

    less.render(lessStr, function (error, cssStr) {
        if (error) {
            console.log(error);
        } else {
            console.log("============")
            console.log(filePath);
            // console.log(typeof lessStr);
            // console.log(lessStr);
            console.log(cssStr);
        }
    })
}

let pwd = process.cwd();
let lessFiles = findLessFiles(pwd)
console.log(lessFiles)

for (let i = 0; i < lessFiles.length; i++) {
    let filePath = lessFiles[i];
    let outPath = filePath.replace(/less$/i, "css");

    compileLessFile(filePath, outPath);
}
