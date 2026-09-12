```markdown
# youtube-video-clipper Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill documents the development patterns and conventions used in the `youtube-video-clipper` Python repository. It covers file organization, code style, import/export patterns, and outlines workflows and testing practices. This guide is intended to help contributors quickly understand and follow the project's established practices.

## Coding Conventions

### File Naming
- **Convention:** Use `snake_case` for all file names.
- **Example:**  
  ```
  video_processor.py
  youtube_downloader.py
  ```

### Import Style
- **Convention:** Use **relative imports** within the package.
- **Example:**
  ```python
  from .video_utils import extract_clip
  from .config import DEFAULT_OUTPUT_PATH
  ```

### Export Style
- **Convention:** Use **named exports** (i.e., define functions/classes and import them explicitly).
- **Example:**
  ```python
  # In video_utils.py
  def extract_clip(input_file, start_time, end_time):
      ...

  # In another module
  from .video_utils import extract_clip
  ```

### Commit Patterns
- **Type:** Freeform (no enforced prefix)
- **Average length:** ~51 characters

## Workflows

### Clipping a YouTube Video
**Trigger:** When you want to extract a specific segment from a YouTube video.
**Command:** `/clip-video`

1. Download the desired YouTube video using the appropriate script/module.
2. Use the `extract_clip` function to specify the start and end times for the segment.
3. Save the clipped segment to the output directory.

**Example:**
```python
from .youtube_downloader import download_video
from .video_utils import extract_clip

video_path = download_video('https://youtube.com/...')
extract_clip(video_path, start_time="00:01:00", end_time="00:02:00")
```

### Adding a New Module
**Trigger:** When you need to add new functionality.
**Command:** `/add-module`

1. Create a new Python file using `snake_case` naming.
2. Implement your functions/classes.
3. Use relative imports to access utilities or shared code.
4. Export functions/classes as named exports.

### Running Tests
**Trigger:** When you want to verify code correctness.
**Command:** `/run-tests`

1. Locate test files (pattern: `*.test.ts`).
2. Run tests using the appropriate test runner (framework is currently unknown; check project documentation or scripts).

## Testing Patterns

- **Test File Pattern:** `*.test.ts`
- **Framework:** Unknown (no framework detected)
- **Notes:** Tests are written in TypeScript, which may indicate a separate test suite or integration with a JS/TS tool. Check for scripts or documentation on how to run tests.

**Example Test File Name:**
```
video_utils.test.ts
```

## Commands
| Command      | Purpose                                    |
|--------------|--------------------------------------------|
| /clip-video  | Extract a segment from a YouTube video     |
| /add-module  | Add a new module following conventions     |
| /run-tests   | Run the test suite                         |
```
