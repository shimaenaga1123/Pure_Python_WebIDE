<script>
    import {
        Card,
        Button,
        LoadingIndicator,
        TextFieldOutlined,
    } from "m3-svelte";
</script>

<div class="loading" id="loading">
    <div class="loading-content">
        <LoadingIndicator />
        <div class="m3-font-body-large">Python 환경 로딩 중...</div>
    </div>
</div>

<div class="container">
    <header class="header">
        <h1 class="m3-font-display-large">Python IDE</h1>
        <p class="m3-font-body-medium">인터랙티브 Python 실행 환경</p>
    </header>

    <main class="main-content">
        <div class="ide-layout">
            <Card variant="filled" id="editor-section">
                <div class="section-header">
                    <h2 class="m3-font-title-medium">코드 에디터</h2>
                </div>
                <div class="editor-wrapper" id="editor"></div>

                <div class="controls">
                    <Button variant="filled" id="runBtn">실행</Button>
                    <Button variant="tonal" id="clearBtn">지우기</Button>
                    <Button variant="outlined" id="clearOutputBtn"
                        >출력 지우기</Button
                    >
                </div>
                <div class="controls">
                    <TextFieldOutlined label="패키지 이름" />
                    <Button variant="filled" id="installBtn">패키지 설치</Button
                    >
                </div>
            </Card>

            <Card variant="filled" id="output-section">
                <div class="section-header">
                    <h2 class="m3-font-title-medium">터미널</h2>
                </div>
                <div class="terminal-wrapper">
                    <div class="output-content" id="output"></div>
                </div>
                <div class="status-bar">
                    <span class="m3-font-label-medium" id="status">준비</span>
                    <span class="m3-font-label-small" id="execTime"></span>
                </div>
            </Card>
        </div>
    </main>
</div>

<style>
    :global(body) {
        margin: 0;
        padding: 0;
        background-color: var(--m3-scheme-background, #1c1b1f);
        color: var(--m3-scheme-on-background, #e6e1e5);
    }

    .loading {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: var(--m3-scheme-surface, #1c1b1f);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        transition:
            opacity 0.3s ease,
            visibility 0.3s ease;
    }

    .loading-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
        color: var(--m3-scheme-on-surface, #e6e1e5);
    }

    .container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 1.5rem;
        min-height: 100vh;
    }

    .header {
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--m3-scheme-outline-variant, #49454f);
    }

    .header h1 {
        margin: 0 0 0.5rem 0;
        color: var(--m3-scheme-on-surface, #e6e1e5);
        font-weight: 400;
    }

    .header p {
        margin: 0;
        color: var(--m3-scheme-on-surface-variant, #cac4d0);
    }

    .main-content {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .ide-layout {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        padding: 1.5rem;
    }

    @media (max-width: 1024px) {
        .ide-layout {
            grid-template-columns: 1fr;
        }
    }

    :global(#editor-section, #output-section) {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        min-height: 600px;
        min-width: 600px;
    }

    .section-header {
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--m3-scheme-outline-variant, #49454f);
    }

    .section-header h2 {
        margin: 0;
        color: var(--m3-scheme-on-surface, #e6e1e5);
        font-weight: 500;
    }

    .editor-wrapper {
        flex: 1;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(
            --m3-util-elevation-1,
            0px 1px 2px rgba(0, 0, 0, 0.3),
            0px 1px 3px 1px rgba(0, 0, 0, 0.15)
        );
        background-color: var(--m3-scheme-surface-container-high, #2b2930);
    }

    :global(.editor-wrapper .cm-editor) {
        height: 100%;
        font-size: 14px;
        font-family: "Fira Code", "Consolas", "Monaco", monospace;
    }

    .controls {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
    }

    .terminal-wrapper {
        flex: 1;
        background-color: var(--m3-scheme-surface-container-highest, #36343b);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(
            --m3-util-elevation-1,
            0px 1px 2px rgba(0, 0, 0, 0.3),
            0px 1px 3px 1px rgba(0, 0, 0, 0.15)
        );
    }

    .output-content {
        padding: 1rem;
        height: 100%;
        overflow-y: scroll;
        font-family: "Fira Code", "Consolas", "Monaco", monospace;
        font-size: 14px;
        line-height: 1.6;
        color: var(--m3-scheme-on-surface, #e6e1e5);
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    .output-content::-webkit-scrollbar {
        width: 12px;
    }

    .output-content::-webkit-scrollbar-track {
        background: var(--m3-scheme-surface-container, #211f26);
        border-radius: 6px;
    }

    .output-content::-webkit-scrollbar-thumb {
        background: var(--m3-scheme-outline, #938f99);
        border-radius: 6px;
        border: 2px solid var(--m3-scheme-surface-container, #211f26);
    }

    .output-content::-webkit-scrollbar-thumb:hover {
        background: var(--m3-scheme-on-surface-variant, #cac4d0);
    }

    :global(.output-content .inline-input) {
        background-color: transparent;
        border: none;
        border-bottom: 2px solid var(--m3-scheme-primary, #d0bcff);
        color: var(--m3-scheme-primary, #d0bcff);
        font-family: inherit;
        font-size: inherit;
        padding: 2px 4px;
        outline: none;
        min-width: 200px;
        caret-color: var(--m3-scheme-primary, #d0bcff);
    }

    :global(.output-content .inline-input:focus) {
        border-bottom-color: var(--m3-scheme-tertiary, #efb8c8);
        box-shadow: 0 2px 0 -1px var(--m3-scheme-tertiary, #efb8c8);
    }

    .status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        background-color: var(--m3-scheme-surface-container-low, #1d1b20);
        border-top: 1px solid var(--m3-scheme-outline-variant, #49454f);
        border-radius: 0 0 12px 12px;
    }

    #status {
        font-weight: 500;
    }

    #execTime {
        color: var(--m3-scheme-on-surface-variant, #cac4d0);
    }

    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
</style>
