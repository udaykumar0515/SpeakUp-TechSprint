import { useAuth } from "@/hooks/use-auth";
import { Link } from "wouter";
import { Layout } from "@/components/layout/Layout";
import { motion } from "framer-motion";
import { Brain, MessageSquare, Users, FileText, ArrowRight, Loader2, Trophy, Clock, Target } from "lucide-react";
import { useDashboardStats } from "@/hooks/use-api";
import { Card, CardContent } from "@/components/ui/card";

const TOOLS = [
  {
    title: "Aptitude Practice",
    description: "Sharpen your logical and quantitative skills with topic-wise quizzes.",
    icon: Brain,
    href: "/aptitude",
    color: "bg-blue-500",
    gradient: "from-blue-500 to-blue-600",
  },
  {
    title: "Mock Interview",
    description: "Practice with AI-driven mock interviews and get instant feedback.",
    icon: MessageSquare,
    href: "/interview",
    color: "bg-purple-500",
    gradient: "from-purple-500 to-purple-600",
  },
  {
    title: "GD Simulator",
    description: "Participate in simulated group discussions with AI bots.",
    icon: Users,
    href: "/gd",
    color: "bg-orange-500",
    gradient: "from-orange-500 to-orange-600",
  },
  {
    title: "Resume Analyzer",
    description: "Upload your resume to check ATS compatibility and get suggestions.",
    icon: FileText,
    href: "/resume",
    color: "bg-emerald-500",
    gradient: "from-emerald-500 to-emerald-600",
  },

];

export default function Dashboard() {
  const { user } = useAuth();
  const { data, isLoading } = useDashboardStats(user?.uid || "");
  const statsResponse = data;

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground">
              Hello, {user?.name.split(" ")[0]}! 👋
            </h1>
            <p className="text-muted-foreground mt-1">Ready to boost your placement preparation today?</p>
          </div>
          {/* Stats Summary */}
          {isLoading ? (
             <div className="flex gap-4">
                <div className="h-10 w-32 bg-muted animate-pulse rounded-xl" />
             </div>
          ) : statsResponse && statsResponse.stats ? (
            <div className="flex gap-4">
              <div className="bg-white px-4 py-2 rounded-xl shadow-sm border text-sm font-medium flex items-center gap-2">
                <Trophy className="w-4 h-4 text-yellow-500" />
                <span>{(statsResponse.stats.totalInterviews + statsResponse.stats.totalGdSessions + statsResponse.stats.totalAptitudeTests)} Sessions</span>
              </div>
              <div className="bg-white px-4 py-2 rounded-xl shadow-sm border text-sm font-medium flex items-center gap-2">
                 <Target className="w-4 h-4 text-blue-500" />
                 <span>Avg Score: {Math.round((statsResponse.stats.averageInterviewScore + statsResponse.stats.averageGdScore + statsResponse.stats.averageAptitudeScore) / 3)}%</span>
              </div>
            </div>
          ) : null}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {TOOLS.map((tool, index) => (
            <Link key={tool.title} href={tool.href}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="group relative overflow-hidden bg-card rounded-2xl p-6 border hover:border-primary/50 shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer h-full"
              >
                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${tool.gradient} opacity-5 rounded-bl-full transform translate-x-8 -translate-y-8`} />
                
                <div className="flex items-start justify-between mb-6">
                  <div className={`w-12 h-12 rounded-xl ${tool.color} flex items-center justify-center shadow-lg shadow-black/5`}>
                    <tool.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="bg-muted px-3 py-1 rounded-full text-xs font-semibold text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                    Start Now
                  </div>
                </div>
                
                <h3 className="text-xl font-bold mb-2 group-hover:text-primary transition-colors">{tool.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{tool.description}</p>
                
                <div className="mt-6 flex items-center text-sm font-medium text-primary opacity-0 group-hover:opacity-100 transition-all transform translate-y-2 group-hover:translate-y-0">
                  Launch Tool <ArrowRight className="w-4 h-4 ml-2" />
                </div>
              </motion.div>
            </Link>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="bg-card rounded-2xl border p-6">
          <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-primary" />
            Recent Activity
          </h3>
          
          {isLoading ? (
             <div className="flex justify-center p-8"><Loader2 className="animate-spin w-8 h-8 text-muted-foreground"/></div>
          ) : statsResponse?.recentActivity && statsResponse.recentActivity.length > 0 ? (
            <div className="space-y-4">
               {statsResponse.recentActivity.map((activity, i) => (
                 <div key={i} className="flex items-center justify-between p-4 bg-muted/20 hover:bg-muted/40 rounded-xl transition-colors border border-transparent hover:border-muted">
                    <div className="flex items-center gap-4">
                       <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white shadow-sm ${
                          activity.type === 'aptitude' ? 'bg-blue-500' : 
                          activity.type === 'interview' ? 'bg-purple-500' : 
                          activity.type === 'gd' ? 'bg-orange-500' : 'bg-emerald-500'
                       }`}>
                          {activity.type === 'aptitude' ? <Brain className="w-5 h-5"/> : 
                           activity.type === 'interview' ? <MessageSquare className="w-5 h-5"/> : 
                           activity.type === 'gd' ? <Users className="w-5 h-5"/> : <FileText className="w-5 h-5"/>}
                       </div>
                       <div>
                          <p className="font-bold text-sm text-foreground">{activity.description}</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(activity.date).toLocaleDateString()} • {new Date(activity.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                       </div>
                    </div>
                    {activity.score !== undefined && (
                        <div className={`text-sm font-bold px-3 py-1 rounded-full ${
                             activity.score >= 80 ? 'bg-green-100 text-green-700' : 
                             activity.score >= 60 ? 'bg-yellow-100 text-yellow-700' : 
                             'bg-red-100 text-red-700'
                        }`}>
                           {activity.score}% Score
                        </div>
                    )}
                 </div>
               ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-32 text-muted-foreground border-2 border-dashed rounded-xl border-muted">
               <p>No recent activity yet. Start your first practice session!</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
