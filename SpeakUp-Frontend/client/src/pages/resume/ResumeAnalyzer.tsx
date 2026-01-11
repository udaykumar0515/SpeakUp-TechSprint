import { useCallback, useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { useUploadResume } from "@/hooks/use-api";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, CheckCircle, AlertTriangle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { useToast } from "@/hooks/use-toast";
import { ResumeUploadResponse } from "@/types/api-types";

export default function ResumeAnalyzer() {
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ResumeUploadResponse | null>(null);
  
  const uploadResume = useUploadResume();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFile(acceptedFiles[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1
  });

  const handleAnalyze = async () => {
    if (!file || !user) return;
    
    // Create Form Data
    const formData = new FormData();
    formData.append("userId", user?.uid || "");
    formData.append("file", file);

    try {
      // Upload and Analyze (backend automatically saves the result)
      const analysisData = await uploadResume.mutateAsync(formData);
      setResult(analysisData);
      
      // ✅ No need for manual save - backend handles it automatically in /api/resume/upload
      
    } catch (error: any) {
      toast({ title: "Analysis Failed", description: error.message, variant: "destructive" });
    }
  };

  return (
    <Layout>
      <div className="max-w-3xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold font-display">Resume Analyzer</h1>
          <p className="text-muted-foreground mt-2">Upload your resume to check ATS compatibility.</p>
        </div>

        {!result ? (
          <Card className="p-8">
            <div 
              {...getRootProps()} 
              className={`border-2 border-dashed rounded-xl h-64 flex flex-col items-center justify-center cursor-pointer transition-colors ${
                isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50"
              }`}
            >
              <input {...getInputProps()} />
              <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-4">
                <UploadCloud className="w-8 h-8" />
              </div>
              {file ? (
                <div className="text-center">
                  <p className="font-bold text-lg text-primary">{file.name}</p>
                  <p className="text-sm text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              ) : (
                <div className="text-center">
                  <p className="font-bold text-lg">Drag & drop or click to upload</p>
                  <p className="text-sm text-muted-foreground">PDF files only (Max 5MB)</p>
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-center">
              <Button 
                size="lg" 
                onClick={handleAnalyze} 
                disabled={!file || uploadResume.isPending}
                className="w-full sm:w-auto min-w-[200px]"
              >
                {uploadResume.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : "Analyze Resume"}
              </Button>
            </div>
          </Card>
        ) : (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <Card className="p-8 text-center bg-gradient-to-br from-white to-blue-50">
              <h2 className="text-xl font-bold mb-4">ATS Score</h2>
              <div className="text-6xl font-black text-primary mb-2">{result.atsScore}/100</div>
              <p className="text-muted-foreground">Your resume is well-optimized!</p>
            </Card>

            <div className="bg-card border rounded-2xl p-6">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" /> Extracted Information
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-muted/30 rounded-lg">
                  <p className="text-xs font-bold text-muted-foreground uppercase">Skills Detected</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {result.parsedData?.skills.map((skill: string) => (
                      <span key={skill} className="bg-primary/10 text-primary text-[10px] px-2 py-0.5 rounded-full font-bold">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="p-4 bg-muted/30 rounded-lg">
                  <p className="text-xs font-bold text-muted-foreground uppercase">Experience Summary</p>
                  <p className="text-sm mt-1">{result.parsedData?.experience || "N/A"}</p>
                </div>
                <div className="p-4 bg-muted/30 rounded-lg md:col-span-2">
                  <p className="text-xs font-bold text-muted-foreground uppercase">Education</p>
                  <p className="text-sm mt-1">{result.parsedData?.education || "N/A"}</p>
                </div>
              </div>
            </div>

            <div className="bg-card border rounded-2xl p-6">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" /> Suggestions for Improvement
              </h3>
              <ul className="space-y-4">
                {result.suggestions.map((suggestion: string, idx: number) => (
                  <li key={idx} className="flex gap-3 items-start p-3 rounded-lg bg-orange-50 text-orange-800">
                    <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
                    <span>{suggestion}</span>
                  </li>
                ))}
                <li className="flex gap-3 items-start p-3 rounded-lg bg-green-50 text-green-800">
                  <CheckCircle className="w-5 h-5 shrink-0 mt-0.5" />
                  <span>Contact information is clear and professional.</span>
                </li>
              </ul>
            </div>

            <div className="flex justify-center">
              <Button variant="outline" onClick={() => { setFile(null); setResult(null); }}>
                Analyze Another Resume
              </Button>
            </div>
          </motion.div>
        )}
      </div>
    </Layout>
  );
}
