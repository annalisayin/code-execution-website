import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

const App: React.FC = () => {
  const [code, setCode] = useState<string>('');
  const [output, setOutput] = useState<string>('');

  const testCode = async () => {
    try {
      const response = await axios.post('http://localhost:8000/test_code', { code });
      setOutput(response.data.output);
    } catch (error: any) {
      setOutput(`Error: ${error.response ? error.response.data.detail : error.message}`);
    }
  };

  const submitCode = async () => {
    try {
      const response = await axios.post('http://localhost:8000/submit_code', { code });
      setOutput(response.data.output);
    } catch (error: any) {
      setOutput(`Error: ${error.response ? error.response.data.detail : error.message}`);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-800">
      <div className="flex-1">
        <Editor
          height="95%"
          width="100%"
          defaultLanguage="python"
          defaultValue="# Write your Python code here"
          onChange={(value) => setCode(value || '')}
          theme="vs-dark"
        />
      </div>
      <div className="flex justify-center space-x-4 p-4 bg-gray-800">
        <button className="btn-primary" onClick={testCode}>
          Test Code
        </button>
        <button className="btn-secondary" onClick={submitCode}>
          Submit
        </button>
      </div>
      <div className="bg-gray-800 text-white p-4">
        <pre>{output}</pre>
      </div>
    </div>
  );
};

export default App;
