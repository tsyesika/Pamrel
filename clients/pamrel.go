package main

import (
    "fmt"
    "flag"
    "os"
    "strings"
    "mime"
    "io/ioutil"
    "encoding/json"
    "net/http"
    "bytes"
)

type Paste struct {
    Id string
    Content string
    FileExtension string
    FileName string
    MimeType string
    Theme string
    Numbers bool
    Syntax bool
}

type Activity struct {
    Verb string
    Object *Paste
}

func paste(path *string, theme string, numbers bool, syntax bool) {
    // Pastes file at path
    new_paste := &Paste{Theme: theme, Numbers: numbers, Syntax: syntax}
    content, _ := ioutil.ReadFile(*path)
    new_paste.Content = string(content)

    files     := strings.Split(*path, "/")
    file      := files[len(files)-1]
    file_type := strings.Split(*path, ".")
    if len(file_type) > 1 {
        new_paste.FileExtension = "." + file_type[1]
    }

    new_paste.FileName = file
    new_paste.MimeType = mime.TypeByExtension(new_paste.FileExtension)

    post_json, err := json.Marshal(new_paste)

    if err != nil {
        fmt.Fprintf(os.Stderr, "Could not encode to JSON (%s)\n", *path)
        os.Exit(3) // couldn't encode to JOSN
    }

    // Post to server
    req, err := http.NewRequest("POST", "http://pamrel.lu", bytes.NewReader(post_json))
    if err != nil {
        fmt.Fprintf(os.Stderr, "Could not post to server\n")
        os.Exit(4) // server error
    }

    // add the headers
    req.Header.Add("User-Agent", "Pamrel CLI client 0.1")
    req.Header.Add("Content-Type", "application/json")

    client := &http.Client{}
    response, _ := client.Do(req)

    defer response.Body.Close() // be a good client
    body, _ := ioutil.ReadAll(response.Body)
    paste := Activity{}

    err = json.Unmarshal(body, &paste)
    if err != nil {
        fmt.Fprintf(os.Stderr, "Could not decode server's response\n")
        fmt.Fprintf(os.Stderr, string(body))
        fmt.Fprintf(os.Stderr, "\n")
        os.Exit(5) // server's response can't be decoded
    }

    fmt.Printf("%s -> http://pamrel.lu/%s\n", *path, paste.Object.Id)
}

func main() {
    // Setup command line options
    var numbers = flag.Bool("numbers", false, "Display line numbers")
    var theme = flag.String("theme", "basic", "Theme used for displaying")
    var syntax = flag.Bool("syntax", true, "Enable syntax highlighting")
    flag.Parse()

    paths := flag.Args()
    if len(paths) <= 0 {
        fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
        flag.PrintDefaults()
        os.Exit(1) // no path specified
    }

    // Check if all the paths are valid
    for _, path := range paths {
        _, err := os.Stat(path)
        if err != nil && os.IsNotExist(err) {
            fmt.Fprintf(os.Stderr, "Cannot find file: %s", path)
            fmt.Println()
            os.Exit(2) // could not find path
        }
        paste(&path, *theme, *numbers, *syntax)
    }
}
